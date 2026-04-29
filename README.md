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
