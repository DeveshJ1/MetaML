# MetaML: Intelligent Multi-Cloud Trading Bot Orchestration Platform

MetaML is a cloud-based Intelligent Autonomous Networked application for orchestrating trading bots in a simulated financial market.

## Phase 0

Current functionality:

- Project repository structure
- Python virtual environment
- RabbitMQ local message bus
- Shared event schemas
- Basic publish/consume smoke test

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d
python scripts/test_consume.py
python scripts/test_publish.py
RabbitMQ Dashboard:http://localhost:15672, metaml / metaml

## Phase 1: Local Market Simulation Loop

Phase 1 adds:

- Synthetic regime-based market replay service
- Simplified market engine
- Baseline trading bot
- Executed trade monitor

### Run Phase 1

Start RabbitMQ:

```bash
docker compose up -d

Then open four terminals:
Go to project directory in each:

cd metaml
source .venv/bin/activate

Terminal 1:
PYTHONPATH=. python services/market-engine/market_engine.py
Terminal 2:
PYTHONPATH=. python services/replay-service/replay_service.py
Terminal 3:
PYTHONPATH=. python services/bots/baseline/baseline_bot.py
Terminal 4:
PYTHONPATH=. python scripts/monitor_trades.py

Expected behavior:

Replay service publishes market snapshots.
Baseline bot receives snapshots.
Baseline bot submits orders.
Market engine executes orders.
Trade monitor displays executed trades.

## Phase 2: Hybrid Market Replay + Logging + PnL

Phase 2 adds:

- Hybrid replay from CSV price data
- Synthetic order book depth
- Market and limit order execution logic
- Trade CSV logging
- Baseline bot PnL tracking

### Run Phase 2

Start RabbitMQ:

```bash
docker compose up -d
Then open 6 different terminals and run:
cd metaml
source .venv/bin/activate

PYTHONPATH=. python services/market-engine/market_engine.py
PYTHONPATH=. python services/replay-service/replay_service.py
PYTHONPATH=. python services/bots/baseline/baseline_bot.py
PYTHONPATH=. python scripts/monitor_trades.py
PYTHONPATH=. python scripts/log_trades.py
PYTHONPATH=. python scripts/track_bot_pnl.py

Exepected Results:
 Replay service reads data/raw/sample_prices.csv
 Market snapshots include source=HYBRID_CSV_REPLAY
 Market snapshots include bid/ask depth
 Market engine receives snapshots
 Baseline bot sends market and limit orders
 Some limit orders fill
 Some limit orders do not fill
 Trade monitor displays trades
 Trade logger writes data/logs/trades.csv
 PnL tracker updates cash, position, and equity

## Phase 3: Multiple Strategy Bots

Phase 3 adds:

- Baseline random bot
- Momentum strategy bot
- Mean reversion strategy bot
- Shared bot utility functions
- All-bot PnL tracker

### Run Phase 3

Start RabbitMQ:

```bash
docker compose up -d
Then open 8 terminals and run each in a separate terminals:
cd metaml
source .venv/bin/activate

PYTHONPATH=. python services/market-engine/market_engine.py
PYTHONPATH=. python services/replay-service/replay_service.py
PYTHONPATH=. python services/bots/baseline/baseline_bot.py
PYTHONPATH=. python services/bots/momentum/momentum_bot.py
PYTHONPATH=. python services/bots/mean-reversion/mean_reversion_bot.py
PYTHONPATH=. python scripts/monitor_trades.py
PYTHONPATH=. python scripts/track_all_pnl.py
PYTHONPATH=. python scripts/log_trades.py

Expectations:
 Baseline bot runs
 Momentum bot runs
 Mean reversion bot runs
 All bots receive market snapshots
 Momentum bot trades on price direction
 Mean reversion bot trades on price deviation
 Market engine executes trades from all bots 
 PnL tracker shows all active bots
 Trade logger can log trades from all bots

## Phase 4: Bot Fingerprints

Phase 4 adds:

- Bot taxonomy metadata
- Fingerprint service
- Time-windowed bot performance summaries
- ML-ready dataset at `data/logs/bot_fingerprints.csv`

### Run Phase 4

```bash
cd metaml
source .venv/bin/activate

docker compose up -d
Then run each in a separate terminal:
PYTHONPATH=. python services/market-engine/market_engine.py
PYTHONPATH=. python services/replay-service/replay_service.py
PYTHONPATH=. python services/bots/baseline/baseline_bot.py
PYTHONPATH=. python services/bots/momentum/momentum_bot.py
PYTHONPATH=. python services/bots/mean-reversion/mean_reversion_bot.py
PYTHONPATH=. python scripts/monitor_trades.py
PYTHONPATH=. python scripts/track_all_pnl.py
PYTHONPATH=. python scripts/log_trades.py
PYTHONPATH=. FINGERPRINT_WINDOW_SECONDS=30 python services/fingerprint/fingerprint_service.py

To view fingerprint summary:
PYTHONPATH=. python scripts/view_fingerprints.py
tail -n 10 data/logs/bot_fingerprints.csv

Expectations:
 bot_taxonomy.json exists
 fingerprint_service.py runs
 fingerprint service receives market snapshots
 fingerprint service receives trades
 service writes data/logs/bot_fingerprints.csv
 each bot has fingerprint rows
 fingerprints include pnl, drawdown, regime, trade count
 view_fingerprints.py summarizes bot performance
## Phase 5: ML Recommendation Model

Phase 5 adds:

- ML training from bot fingerprints
- Saved model artifact
- FastAPI inference service
- Recommendation endpoint
- Scripts to test recommendations

### Train Model
Must have results from Phase 4:
```bash
PYTHONPATH=. python services/inference/train_model.py

Start Inference API:
PYTHONPATH=. uvicorn services.inference.inference_api:app --host 0.0.0.0 --port 8000
Health Check : curl http://localhost:8000/health

Test Recommendation:
PYTHONPATH=. python scripts/test_recommendation.py

Recommendation from latest fingerprints:
PYTHONPATH=. python scripts/recommend_from_latest_fingerprints.py

Expectations:
 bot_fingerprints.csv has data
 train_model.py runs
 data/models/bot_recommender.pkl is created
 inference_api.py starts with uvicorn
 /health returns model_loaded true
 /recommend returns recommended_bot
 test_recommendation.py works
 recommend_from_latest_fingerprints.py works

## Phase 6: MetaML Orchestrator

Phase 6 adds:

- Orchestrator service
- ML recommendation polling
- Manual human-in-the-loop approval
- Auto-switch mode
- Active bot state file
- Orchestrator decision log

### Run Orchestrator
Must have Results from 4/5. 
Manual mode:

```bash
PYTHONPATH=. ORCHESTRATOR_MODE=manual ORCHESTRATOR_POLL_SECONDS=15 python services/orchestrator/orchestrator.py

Auto Mode:

PYTHONPATH=. ORCHESTRATOR_MODE=auto ORCHESTRATOR_POLL_SECONDS=15 python services/orchestrator/orchestrator.py

Run Once (no looping):
PYTHONPATH=. ORCHESTRATOR_MODE=manual python scripts/test_orchestrator_once.py

View Active Bot:
PYTHONPATH=. python scripts/view_active_bot.py

View Decisions:
PYTHONPATH=. python scripts/view_orchestrator_decisions.py

Expectations:
 orchestrator.py starts
 it reads latest bot fingerprints
 it calls inference API
 it receives recommended_bot
 manual mode asks for approval
 auto mode switches automatically
 active_bot.json is created
 orchestrator_decisions.csv is created
 view_active_bot.py works
 view_orchestrator_decisions.py works
