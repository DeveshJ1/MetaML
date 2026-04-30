import os
import pandas as pd

PATH = "data/logs/bot_fingerprints.csv"

if not os.path.exists(PATH):
    print(f"No fingerprint file found at {PATH}")
    raise SystemExit(1)

df = pd.read_csv(PATH)

if df.empty:
    print("Fingerprint file exists but is empty.")
    raise SystemExit(0)

print("\nLatest fingerprints:")
print(df.tail(10).to_string(index=False))

print("\nAverage PnL by bot:")
print(df.groupby("bot_id")["pnl"].mean().sort_values(ascending=False).to_string())

print("\nAverage PnL by bot and regime:")
print(df.groupby(["bot_id", "market_regime"])["pnl"].mean().sort_values(ascending=False).to_string())
