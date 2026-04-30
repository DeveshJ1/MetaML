import json
import os

ACTIVE_STATE_PATH = "services/orchestrator/state/active_bot.json"

def get_active_bot():
    if not os.path.exists(ACTIVE_STATE_PATH):
        return None

    try:
        with open(ACTIVE_STATE_PATH, "r") as f:
            state = json.load(f)
        return state.get("active_bot")
    except Exception:
        return None

def is_active_bot(bot_id):
    active_bot = get_active_bot()
    return active_bot == bot_id
