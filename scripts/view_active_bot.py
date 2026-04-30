import json
import os

PATH = "services/orchestrator/state/active_bot.json"

if not os.path.exists(PATH):
    print("No active bot state found yet.")
    raise SystemExit(0)

with open(PATH, "r") as f:
    state = json.load(f)

print(json.dumps(state, indent=2))
