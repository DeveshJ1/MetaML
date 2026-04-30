import os
import pandas as pd
import requests

PATH = "data/logs/bot_fingerprints.csv"
URL = "http://localhost:8000/recommend"

if not os.path.exists(PATH):
    print(f"Missing {PATH}")
    raise SystemExit(1)

df = pd.read_csv(PATH)

if df.empty:
    print("Fingerprint file is empty.")
    raise SystemExit(1)

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

resp = requests.post(URL, json={"candidates": candidates})

print("Latest candidate bots:")
print(latest[["bot_id", "strategy_type", "market_regime", "pnl", "drawdown", "trade_count"]].to_string(index=False))

print("\nRecommendation:")
print(resp.json())
