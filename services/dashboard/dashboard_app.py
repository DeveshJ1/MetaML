import json
import os
import time
from datetime import datetime, timezone

import pandas as pd
from fastapi import FastAPI, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

ACTIVE_STATE_PATH = "services/orchestrator/state/active_bot.json"
FINGERPRINT_PATH = "data/logs/bot_fingerprints.csv"
DECISION_PATH = "data/logs/orchestrator_decisions.csv"
TRADES_PATH = "data/logs/trades.csv"
REGISTRY_PATH = "data/registry/service_registry.json"
AUDIT_PATH = "data/audit/audit_chain.csv"

VALID_BOTS = ["baseline-bot", "momentum-bot", "mean-reversion-bot", "none"]

app = FastAPI(title="MetaML Dashboard")
templates = Jinja2Templates(directory="services/dashboard/templates")

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def read_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default

def read_csv_tail(path, n=10):
    if not os.path.exists(path):
        return []
    try:
        df = pd.read_csv(path)
        if df.empty:
            return []
        return df.tail(n).fillna("").to_dict(orient="records")
    except Exception:
        return []

def read_latest_fingerprints():
    if not os.path.exists(FINGERPRINT_PATH):
        return []

    try:
        df = pd.read_csv(FINGERPRINT_PATH)
        if df.empty:
            return []

        latest = (
            df.sort_values("window_end")
              .groupby("bot_id", as_index=False)
              .tail(1)
        )

        return latest.fillna("").to_dict(orient="records")
    except Exception:
        return []

def summarize_trades():
    if not os.path.exists(TRADES_PATH):
        return {
            "trade_count": 0,
            "latest_price": None,
            "latest_regime": None
        }

    try:
        df = pd.read_csv(TRADES_PATH)
        if df.empty:
            return {
                "trade_count": 0,
                "latest_price": None,
                "latest_regime": None
            }

        latest = df.tail(1).iloc[0]

        return {
            "trade_count": len(df),
            "latest_price": latest.get("price"),
            "latest_regime": latest.get("market_regime")
        }
    except Exception:
        return {
            "trade_count": 0,
            "latest_price": None,
            "latest_regime": None
        }

def set_active_bot(bot):
    active_bot = None if bot == "none" else bot

    state = {
        "active_bot": active_bot,
        "last_switch_time": time.time(),
        "last_decision": {
            "timestamp": utc_now(),
            "decision": "DASHBOARD_MANUAL_SET",
            "recommendation": {
                "recommended_bot": active_bot
            }
        }
    }

    os.makedirs(os.path.dirname(ACTIVE_STATE_PATH), exist_ok=True)

    with open(ACTIVE_STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

@app.get("/")
def dashboard(request: Request):
    active_state = read_json(ACTIVE_STATE_PATH, {
        "active_bot": None,
        "last_decision": None
    })

    fingerprints = read_latest_fingerprints()
    decisions = read_csv_tail(DECISION_PATH, 8)
    trades = read_csv_tail(TRADES_PATH, 8)
    trade_summary = summarize_trades()
    registry = read_json(REGISTRY_PATH, {})
    audit_events = read_csv_tail(AUDIT_PATH, 8)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "active_state": active_state,
            "fingerprints": fingerprints,
            "decisions": decisions,
            "trades": trades,
            "trade_summary": trade_summary,
            "valid_bots": VALID_BOTS,
            "registry": registry,
            "audit_events": audit_events
        }
    )

@app.post("/set-active-bot")
def set_active_bot_route(bot: str = Form(...)):
    if bot not in VALID_BOTS:
        return RedirectResponse("/", status_code=303)

    set_active_bot(bot)
    return RedirectResponse("/", status_code=303)

@app.get("/health")
def health():
    return {"status": "ok"}
