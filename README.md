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

