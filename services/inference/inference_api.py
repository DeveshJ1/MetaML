import os
import pickle
from typing import List, Dict, Any

import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

MODEL_PATH = os.getenv("MODEL_PATH", "data/models/bot_recommender.pkl")

app = FastAPI(title="MetaML Bot Recommendation API")

artifact = None

class CandidateBot(BaseModel):
    bot_id: str
    strategy_type: str
    risk_profile: str
    market_regime: str
    trade_count: float = 0
    buy_count: float = 0
    sell_count: float = 0
    net_position: float = 0
    pnl: float = 0
    drawdown: float = 0
    fill_rate: float = 0
    avg_trade_size: float = 0
    avg_execution_price: float = 0
    price_volatility: float = 0

class RecommendationRequest(BaseModel):
    candidates: List[CandidateBot]

@app.on_event("startup")
def load_model():
    global artifact

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. Run train_model.py first."
        )

    with open(MODEL_PATH, "rb") as f:
        artifact = pickle.load(f)

    print(f"[inference-api] Loaded model from {MODEL_PATH}")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": artifact is not None
    }

@app.post("/recommend")
def recommend(req: RecommendationRequest) -> Dict[str, Any]:
    if not req.candidates:
        return {
            "recommended_bot": None,
            "reason": "No candidates provided",
            "rankings": []
        }

    features = artifact["features"]
    pipeline = artifact["pipeline"]

    rows = [candidate.dict() for candidate in req.candidates]
    df = pd.DataFrame(rows)

    for feature in features:
        if feature not in df.columns:
            df[feature] = 0

    df = df[features]

    if hasattr(pipeline.named_steps["model"], "predict_proba"):
        probs = pipeline.predict_proba(df)

        # Find probability of True class if present.
        classes = list(pipeline.named_steps["model"].classes_)

        if True in classes:
            true_idx = classes.index(True)
            scores = probs[:, true_idx]
        else:
            scores = probs[:, 0]
    else:
        preds = pipeline.predict(df)
        scores = [1.0 if pred else 0.0 for pred in preds]

    rankings = []

    for row, score in zip(rows, scores):
        rankings.append({
            "bot_id": row["bot_id"],
            "strategy_type": row["strategy_type"],
            "score": float(score),
            "market_regime": row["market_regime"],
            "pnl": row["pnl"],
            "drawdown": row["drawdown"]
        })

    rankings = sorted(rankings, key=lambda x: x["score"], reverse=True)
    best = rankings[0]

    return {
        "recommended_bot": best["bot_id"],
        "recommended_strategy": best["strategy_type"],
        "confidence_score": best["score"],
        "rankings": rankings
    }
