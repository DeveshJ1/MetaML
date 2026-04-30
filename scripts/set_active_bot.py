import json
import os
import sys
import time
from datetime import datetime, timezone

VALID_BOTS = {
    "baseline-bot",
    "momentum-bot",
    "mean-reversion-bot",
    "none"
}

PATH = "services/orchestrator/state/active_bot.json"

def utc_now():
    return datetime.now(timezone.utc).isoformat()

if len(sys.argv) != 2:
    print("Usage:")
    print("  PYTHONPATH=. python scripts/set_active_bot.py baseline-bot")
    print("  PYTHONPATH=. python scripts/set_active_bot.py momentum-bot")
    print("  PYTHONPATH=. python scripts/set_active_bot.py mean-reversion-bot")
    print("  PYTHONPATH=. python scripts/set_active_bot.py none")
    raise SystemExit(1)

bot = sys.argv[1]

if bot not in VALID_BOTS:
    print(f"Invalid bot: {bot}")
    print(f"Valid options: {sorted(VALID_BOTS)}")
    raise SystemExit(1)

active_bot = None if bot == "none" else bot

state = {
    "active_bot": active_bot,
    "last_switch_time": time.time(),
    "last_decision": {
        "timestamp": utc_now(),
        "decision": "MANUAL_SET",
        "recommendation": {
            "recommended_bot": active_bot
        }
    }
}

os.makedirs(os.path.dirname(PATH), exist_ok=True)

with open(PATH, "w") as f:
    json.dump(state, f, indent=2)

print(f"Set active_bot to: {active_bot}")
