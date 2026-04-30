import os
import pandas as pd

PATH = "data/logs/orchestrator_decisions.csv"

if not os.path.exists(PATH):
    print("No orchestrator decision log found yet.")
    raise SystemExit(0)

df = pd.read_csv(PATH)

if df.empty:
    print("Decision log exists but is empty.")
    raise SystemExit(0)

print("\nLatest orchestrator decisions:")
print(df.tail(10).to_string(index=False))
