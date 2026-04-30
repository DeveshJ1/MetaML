import csv
import json
import os
import time
from datetime import datetime, timezone

import pandas as pd
import requests

FINGERPRINT_PATH = "data/logs/bot_fingerprints.csv"
DECISION_LOG = "data/logs/orchestrator_decisions.csv"
ACTIVE_STATE_PATH = "services/orchestrator/state/active_bot.json"

INFERENCE_URL = os.getenv("INFERENCE_URL", "http://localhost:8000/recommend")
ORCHESTRATOR_MODE = os.getenv("ORCHESTRATOR_MODE", "manual")  # manual or auto
POLL_SECONDS = int(os.getenv("ORCHESTRATOR_POLL_SECONDS", "15"))

COOLDOWN_SECONDS = int(os.getenv("ORCHESTRATOR_COOLDOWN_SECONDS", "30"))
MIN_CONFIDENCE = float(os.getenv("ORCHESTRATOR_MIN_CONFIDENCE", "0.50"))

FIELDS = [
    "timestamp",
    "mode",
    "previous_active_bot",
    "recommended_bot",
    "recommended_strategy",
    "confidence_score",
    "decision",
    "reason"
]

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def ensure_decision_log():
    os.makedirs(os.path.dirname(DECISION_LOG), exist_ok=True)
    if not os.path.exists(DECISION_LOG):
        with open(DECISION_LOG, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()

def load_active_state():
    if not os.path.exists(ACTIVE_STATE_PATH):
        state = {
            "active_bot": None,
            "last_switch_time": 0,
            "last_decision": None
        }
        save_active_state(state)
        return state

    with open(ACTIVE_STATE_PATH, "r") as f:
        return json.load(f)

def save_active_state(state):
    os.makedirs(os.path.dirname(ACTIVE_STATE_PATH), exist_ok=True)
    with open(ACTIVE_STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

def log_decision(row):
    with open(DECISION_LOG, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writerow(row)

def load_latest_candidates():
    if not os.path.exists(FINGERPRINT_PATH):
        print(f"[orchestrator] Missing {FINGERPRINT_PATH}. Waiting...")
        return []

    df = pd.read_csv(FINGERPRINT_PATH)

    if df.empty:
        print("[orchestrator] Fingerprint file empty. Waiting...")
        return []

    latest = (
        df.sort_values("window_end")
          .groupby("bot_id", as_index=False)
          .tail(1)
    )

    candidates = []

    for _, row in latest.iterrows():
        candidates.append({
            "bot_id": row["bot_id"],
            "strategy_type": row["strategy_type"],
            "risk_profile": row["risk_profile"],
            "market_regime": row["market_regime"],
            "trade_count": float(row["trade_count"]),
            "buy_count": float(row["buy_count"]),
            "sell_count": float(row["sell_count"]),
            "net_position": float(row["net_position"]),
            "pnl": float(row["pnl"]),
            "drawdown": float(row["drawdown"]),
            "fill_rate": float(row["fill_rate"]),
            "avg_trade_size": float(row["avg_trade_size"]),
            "avg_execution_price": float(row["avg_execution_price"]),
            "price_volatility": float(row["price_volatility"])
        })

    return candidates

def get_recommendation(candidates):
    response = requests.post(INFERENCE_URL, json={"candidates": candidates}, timeout=10)
    response.raise_for_status()
    return response.json()

def guardrail_check(state, recommendation):
    previous = state.get("active_bot")
    recommended = recommendation.get("recommended_bot")
    confidence = float(recommendation.get("confidence_score", 0.0))

    now = time.time()
    last_switch = float(state.get("last_switch_time", 0))

    if recommended is None:
        return "REJECT", "No recommended bot returned"

    if confidence < MIN_CONFIDENCE:
        return "REJECT", f"Confidence {confidence:.2f} below threshold {MIN_CONFIDENCE:.2f}"

    if previous == recommended:
        return "KEEP", "Recommended bot already active"

    if now - last_switch < COOLDOWN_SECONDS:
        return "REJECT", f"Cooldown active: {int(now - last_switch)}s elapsed, need {COOLDOWN_SECONDS}s"

    return "SWITCH", "Recommendation passed guardrails"

def apply_decision(state, recommendation, decision):
    recommended = recommendation.get("recommended_bot")

    if decision == "SWITCH":
        state["active_bot"] = recommended
        state["last_switch_time"] = time.time()

    state["last_decision"] = {
        "timestamp": utc_now(),
        "decision": decision,
        "recommendation": recommendation
    }

    save_active_state(state)

def prompt_manual_approval(previous, recommended, strategy, confidence):
    print("\n[orchestrator] Manual approval required")
    print(f"Previous active bot: {previous}")
    print(f"Recommended bot:     {recommended}")
    print(f"Strategy:            {strategy}")
    print(f"Confidence:          {confidence:.4f}")
    answer = input("Approve switch? [y/N]: ").strip().lower()
    return answer == "y"

def run_once():
    ensure_decision_log()
    state = load_active_state()

    candidates = load_latest_candidates()
    if not candidates:
        return

    try:
        recommendation = get_recommendation(candidates)
    except Exception as e:
        print(f"[orchestrator] Inference request failed: {e}")
        return

    previous = state.get("active_bot")
    recommended = recommendation.get("recommended_bot")
    strategy = recommendation.get("recommended_strategy")
    confidence = float(recommendation.get("confidence_score", 0.0))

    decision, reason = guardrail_check(state, recommendation)

    if decision == "SWITCH" and ORCHESTRATOR_MODE == "manual":
        approved = prompt_manual_approval(previous, recommended, strategy, confidence)
        if approved:
            decision = "SWITCH"
            reason = "Human approved switch"
        else:
            decision = "REJECT"
            reason = "Human rejected switch"

    apply_decision(state, recommendation, decision)

    log_row = {
        "timestamp": utc_now(),
        "mode": ORCHESTRATOR_MODE,
        "previous_active_bot": previous,
        "recommended_bot": recommended,
        "recommended_strategy": strategy,
        "confidence_score": confidence,
        "decision": decision,
        "reason": reason
    }

    log_decision(log_row)

    print("\n[orchestrator] Decision")
    print("-" * 70)
    print(f"Mode:           {ORCHESTRATOR_MODE}")
    print(f"Previous bot:   {previous}")
    print(f"Recommended:    {recommended}")
    print(f"Strategy:       {strategy}")
    print(f"Confidence:     {confidence:.4f}")
    print(f"Decision:       {decision}")
    print(f"Reason:         {reason}")
    print(f"Active bot now: {load_active_state().get('active_bot')}")
    print("-" * 70)

def main():
    print("[orchestrator] Starting MetaML Orchestrator")
    print(f"[orchestrator] Mode: {ORCHESTRATOR_MODE}")
    print(f"[orchestrator] Poll interval: {POLL_SECONDS}s")
    print(f"[orchestrator] Inference URL: {INFERENCE_URL}")

    while True:
        try:
            run_once()
            time.sleep(POLL_SECONDS)
        except KeyboardInterrupt:
            print("[orchestrator] Stopping...")
            break

if __name__ == "__main__":
    main()
