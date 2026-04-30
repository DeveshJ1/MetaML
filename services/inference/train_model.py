import os
import pickle

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

DATA_PATH = "data/logs/bot_fingerprints.csv"
MODEL_PATH = "data/models/bot_recommender.pkl"

FEATURES = [
    "bot_id",
    "strategy_type",
    "risk_profile",
    "market_regime",
    "trade_count",
    "buy_count",
    "sell_count",
    "net_position",
    "pnl",
    "drawdown",
    "fill_rate",
    "avg_trade_size",
    "avg_execution_price",
    "price_volatility"
]

TARGET = "recommended_for_future"

CATEGORICAL = [
    "bot_id",
    "strategy_type",
    "risk_profile",
    "market_regime"
]

NUMERIC = [
    "trade_count",
    "buy_count",
    "sell_count",
    "net_position",
    "pnl",
    "drawdown",
    "fill_rate",
    "avg_trade_size",
    "avg_execution_price",
    "price_volatility"
]

def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Missing dataset: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    if df.empty:
        raise RuntimeError("Fingerprint dataset is empty.")

    df = df.dropna(subset=FEATURES + [TARGET])

    if len(df) < 10:
        print("[train-model] WARNING: Dataset is small. Let Phase 4 run longer for better ML results.")

    df[TARGET] = df[TARGET].astype(str).str.lower().isin(["true", "1", "yes"])

    X = df[FEATURES]
    y = df[TARGET]

    if y.nunique() < 2:
        print("[train-model] WARNING: Only one class found in target.")
        print("[train-model] Creating a fallback rule-like model may be better after more data.")
        print("[train-model] Let the system run longer until both True and False recommendations exist.")

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
            ("num", "passthrough", NUMERIC)
        ]
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced"
    )

    pipeline = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", model)
        ]
    )

    if len(df) >= 20 and y.nunique() >= 2:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.25,
            random_state=42,
            stratify=y
        )

        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)

        print("[train-model] Accuracy:", accuracy_score(y_test, preds))
        print("[train-model] Classification report:")
        print(classification_report(y_test, preds))
    else:
        pipeline.fit(X, y)
        print("[train-model] Trained on full dataset because dataset is small.")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    artifact = {
        "pipeline": pipeline,
        "features": FEATURES,
        "categorical": CATEGORICAL,
        "numeric": NUMERIC,
        "target": TARGET
    }

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(artifact, f)

    print(f"[train-model] Saved model to {MODEL_PATH}")
    print(f"[train-model] Rows used: {len(df)}")
    print("[train-model] Label counts:")
    print(y.value_counts())

if __name__ == "__main__":
    main()
