# MetaML: Intelligent Multi-Cloud Trading Bot Orchestration Platform

MetaML is a cloud-based Intelligent Autonomous Networked (IAN) application for orchestrating trading bots in a simulated financial market. The platform combines distributed systems, machine learning, event-driven architecture, and multi-cloud deployment to dynamically select and manage trading strategies.

The system simulates market activity, generates trading telemetry, computes bot performance fingerprints, trains an ML recommendation model, and autonomously activates the best-performing strategy through an orchestration layer.

---

# Features

- Simulated financial market environment
- Multiple trading strategies
  - Baseline random bot
  - Momentum bot
  - Mean-reversion bot
- Event-driven architecture using RabbitMQ
- Market replay and trade execution engine
- Bot fingerprint generation and analytics
- ML-based strategy recommendation system
-  Autonomous orchestrator with human-in-the-loop support
- Operator dashboard
- Decentralized-style service registry
- Tamper-evident audit chain
- Dockerized full-system deployment
- Multi-cloud deployment across AWS, GCP, and Azure
- Cloud-native managed data services integration

---

# System Architecture

## High-Level Flow

```text
Market Replay
      ↓
Trading Bots
      ↓
Market Engine
      ↓
Trade Logs
      ↓
Fingerprint Service
      ↓
ML Inference API
      ↓
Orchestrator
      ↓
Active Bot Control
      ↓
Dashboard + Registry + Audit
```

---

# Node Categories

The project is organized into node categories following IAN principles.

| Node Category | Components |
|---|---|
| Market Infrastructure Nodes | Replay service, market engine |
| Trading Bot Nodes | Baseline, momentum, mean-reversion bots |
| Intelligence Nodes | Fingerprint service, ML inference API |
| Orchestration Nodes | Orchestrator service |
| Monitoring Nodes | Dashboard |
| Registry & Audit Nodes | Registry API, audit API |

---

# Technology Stack

| Category | Technologies |
|---|---|
| Language | Python |
| Messaging | RabbitMQ |
| APIs | FastAPI |
| ML | scikit-learn |
| Containers | Docker, Docker Compose |
| AWS | App Runner, S3, Athena, ECR |
| GCP | Cloud Run, BigQuery, Artifact Registry |
| Azure | Container Apps, Cosmos DB, ACR |

---

# Repository Structure

```text
metaml/
|
|-- services/
|   |-- replay-service/
|   |-- market-engine/
|   |-- bots/
|   |-- fingerprint/
|   |-- inference/
|   |-- orchestrator/
|   |-- dashboard/
|   |-- registry/
|   |-- audit/
|
|-- shared/
|   |-- libs/
|   |-- schemas/
|
|-- scripts/
|-- data/
|-- docs/
|-- final_submission/
|-- docker-compose.yml
```

---

# Quick Start

## Clone Repository

```bash
git clone <repository-url>
cd metaml
```

## Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Start RabbitMQ

```bash
docker compose up -d rabbitmq
```

RabbitMQ UI:

```text
http://localhost:15672
```

Credentials:

```text
metaml / metaml
```

---

# Full Dockerized Demo

Train model first:

```bash
PYTHONPATH=. python services/inference/train_model.py
```

Run full system:

```bash
docker compose up --build
```

---

# Local URLs

| Service | URL |
|---|---|
| Dashboard | http://localhost:8501 |
| Inference API | http://localhost:8000/health |
| Registry API | http://localhost:8600/services |
| Audit API | http://localhost:8700/audit/verify |
| RabbitMQ UI | http://localhost:15672 |

---

# Project Phases

## Phase 0 - Local Infrastructure Setup

### Added

- Project structure
- Python virtual environment
- RabbitMQ messaging backbone
- Shared event schemas
- Publish/consume smoke tests

### Key Commands

```bash
docker compose up -d
python scripts/test_consume.py
python scripts/test_publish.py
```

---

## Phase 1 - Local Market Simulation Loop

### Added

- Synthetic market replay service
- Simplified market engine
- Baseline trading bot
- Trade monitoring

### Result

The replay service publishes market snapshots, the baseline bot submits orders, and the market engine executes trades.

---

## Phase 2 - Hybrid Replay + Logging + PnL

### Added

- CSV-based market replay
- Synthetic order book depth
- Market and limit orders
- Trade CSV logging
- Bot PnL tracking

### Result

Trades and portfolio metrics are persisted locally for analytics and ML processing.

---

## Phase 3 - Multiple Trading Strategies

### Added

- Baseline bot
- Momentum bot
- Mean-reversion bot
- Shared bot utility libraries
- Multi-bot PnL tracking

### Result

Multiple strategies operate simultaneously and respond differently to market conditions.

---

## Phase 4 - Bot Fingerprinting

### Added

- Bot taxonomy metadata
- Fingerprint service
- Rolling performance summaries
- ML-ready fingerprint dataset

### Generated Dataset

```text
data/logs/bot_fingerprints.csv
```

### Fingerprint Metrics

- PnL
- Drawdown
- Trade count
- Volatility
- Market regime
- Position exposure

---

## Phase 5 - ML Recommendation System

### Added

- ML training pipeline
- Saved model artifact
- FastAPI inference service
- Recommendation scripts

### Training

```bash
PYTHONPATH=. python services/inference/train_model.py
```

### Start Inference API

```bash
PYTHONPATH=. uvicorn services.inference.inference_api:app --host 0.0.0.0 --port 8000
```

### Test Recommendation

```bash
PYTHONPATH=. python scripts/recommend_from_latest_fingerprints.py
```

---

## Phase 6 - MetaML Orchestrator

### Added

- Orchestrator service
- ML recommendation polling
- Human-in-the-loop approval
- Automatic orchestration mode
- Active bot state management
- Orchestrator decision logs

### Manual Mode

```bash
PYTHONPATH=. ORCHESTRATOR_MODE=manual python services/orchestrator/orchestrator.py
```

### Automatic Mode

```bash
PYTHONPATH=. ORCHESTRATOR_MODE=auto python services/orchestrator/orchestrator.py
```

---

## Phase 7 - Active Bot Control

### Added

- Active bot state management
- Orchestrator-controlled trading
- Manual active bot switching

### Set Active Bot

```bash
PYTHONPATH=. python scripts/set_active_bot.py baseline-bot
PYTHONPATH=. python scripts/set_active_bot.py momentum-bot
PYTHONPATH=. python scripts/set_active_bot.py mean-reversion-bot
```

### Result

Only the active strategy is allowed to trade.

---

## Phase 8 - Operator Dashboard

### Added

- FastAPI dashboard
- Active bot monitoring
- Manual bot switching
- Trade and fingerprint visualization
- Orchestrator decision visualization

### Start Dashboard

```bash
PYTHONPATH=. uvicorn services.dashboard.dashboard_app:app --host 0.0.0.0 --port 8501
```

Open:

```text
http://localhost:8501
```

---

## Phase 9 - Registry + Audit Layer

### Added

- Decentralized-style service registry
- Registry API
- Tamper-evident audit chain
- Audit verification API

### Registry API

```bash
PYTHONPATH=. uvicorn services.registry.registry_api:app --host 0.0.0.0 --port 8600
```

### Audit API

```bash
PYTHONPATH=. uvicorn services.audit.audit_api:app --host 0.0.0.0 --port 8700
```

### Result

The system supports service discovery and audit verification.

---

## Phase 10 - Dockerized Full-System Deployment

### Added

- Dockerfiles
- Full Docker Compose stack
- One-command local deployment

### Containerized Services

- RabbitMQ
- Replay service
- Market engine
- Trading bots
- Fingerprint service
- Inference API
- Orchestrator
- Dashboard
- Registry API
- Audit API

### Run Full System

```bash
docker compose up --build
```

---

## Phase 11 - Multi-Cloud Deployment

The project deploys services across AWS, GCP, and Azure.

| Cloud | Service | Purpose |
|---|---|---|
| AWS | App Runner | Registry API |
| GCP | Cloud Run | ML Inference API |
| Azure | Container Apps | Dashboard |

---

## AWS Deployment

### Services Used

- App Runner
- Amazon ECR

### Purpose

Hosts the decentralized-style registry API.

---

## GCP Deployment

### Services Used

- Cloud Run
- Artifact Registry

### Purpose

Hosts the ML inference API.

---

## Azure Deployment

### Services Used

- Azure Container Apps
- Azure Container Registry

### Purpose

Hosts the operator dashboard.

---

## Phase 11.5 - Cloud Data Services Integration

This phase extends the system with cloud-native managed data services.

---

## Final Cloud Data Architecture

| Cloud | Services | Purpose |
|---|---|---|
| AWS | S3 + Athena | Trade telemetry and SQL analytics |
| GCP | BigQuery | Bot analytics and orchestration analysis |
| Azure | Cosmos DB | Metadata and orchestration records |

---

## AWS - S3 + Athena

### Purpose

Stores raw telemetry files and enables SQL-based analytics.

### Uploaded Data

- `trades.csv`
- `bot_fingerprints.csv`
- `orchestrator_decisions.csv`

### Athena Query Example

```sql
SELECT symbol, market_regime,
       AVG(price) AS avg_price,
       COUNT(*) AS trades
FROM metaml_telemetry.trades
GROUP BY symbol, market_regime;
```

### Important Note

AWS Timestream was originally planned but the AWS account did not have LiveAnalytics access, so the telemetry layer was adapted to use S3 + Athena.

---

## GCP - BigQuery

### Purpose

Stores analytics-ready datasets for evaluating bot performance.

### Tables

- bot_fingerprints
- orchestrator_decisions
- trades

### Export Script

```bash
GCP_PROJECT_ID=<project-id> PYTHONPATH=. python scripts/cloud_exports/export_to_bigquery.py
```

---

## Azure - Cosmos DB

### Purpose

Stores JSON-based metadata and orchestration records.

### Containers

- bot_taxonomy
- bot_fingerprints
- orchestrator_decisions

### Export Script

```bash
COSMOS_ENDPOINT=<endpoint> \
COSMOS_KEY=<key> \
PYTHONPATH=. python scripts/cloud_exports/export_to_cosmos.py
```

---

# Demo Workflow

The final demo follows this flow:

1. Start the simulated market
2. Run all bots to generate fingerprints
3. Train ML recommendation model
4. Start inference API
5. Start orchestrator
6. Activate best-performing strategy
7. Monitor system through dashboard
8. Verify cloud deployments
9. Query cloud data services

---

# Intelligent Autonomous Loop

```text
Observe → Analyze → Predict → Decide → Act
```

| Stage | Description |
|---|---|
| Observe | Collect market snapshots and trades |
| Analyze | Generate bot fingerprints |
| Predict | ML model recommends strategy |
| Decide | Orchestrator evaluates recommendation |
| Act | Active bot is updated |

---

# Registry and Audit Design

## Registry

The registry stores service descriptors and enables decentralized-style service discovery.

## Audit Chain

The audit chain uses hash-linked records to create tamper-evident orchestration logs.

---

# Final Cloud Architecture

```text
AWS:
  App Runner + S3/Athena

GCP:
  Cloud Run + BigQuery

Azure:
  Container Apps + Cosmos DB
```

---

# Cleanup

## Stop Local System

```bash
docker compose down
```

## Cloud Cleanup

See:

```text
final_submission/demo/cloud_cleanup_guide.md
```

---

# Future Work

- Real-time cloud streaming pipelines
- Stronger ML models
- Full P2P networking
- Kubernetes deployment
- Authentication and security hardening
- More advanced trading strategies

---

# Conclusion

MetaML demonstrates:

- Intelligent Autonomous Networked architecture
- Distributed event-driven design
- Machine-learning-driven orchestration
- Human-in-the-loop control
- Multi-cloud deployment
- Cloud-native data integration
- Registry and audit functionality

The project satisfies the core course requirements for a cloud-based IAN application deployed across multiple cloud providers.

