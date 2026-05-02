from shared.libs.service_registry import register_service

services = [
    {
        "service_id": "rabbitmq-message-bus",
        "service_type": "event_bus",
        "endpoint": "amqp://localhost:5672",
        "cloud": "local-dev",
        "metadata": {
            "dashboard": "http://localhost:15672",
            "topics": ["orders.new", "trade.executed", "market.snapshot"]
        }
    },
    {
        "service_id": "market-engine",
        "service_type": "market_infrastructure_node",
        "endpoint": "local-process:services/market-engine/market_engine.py",
        "cloud": "aws-target",
        "metadata": {
            "role": "matching_engine",
            "symbols": ["AAPL"]
        }
    },
    {
        "service_id": "replay-service",
        "service_type": "market_replay_node",
        "endpoint": "local-process:services/replay-service/replay_service.py",
        "cloud": "aws-target",
        "metadata": {
            "source": "hybrid_csv_replay"
        }
    },
    {
        "service_id": "baseline-bot",
        "service_type": "execution_node",
        "endpoint": "local-process:services/bots/baseline/baseline_bot.py",
        "cloud": "aws-target",
        "metadata": {
            "strategy": "baseline_random"
        }
    },
    {
        "service_id": "momentum-bot",
        "service_type": "execution_node",
        "endpoint": "local-process:services/bots/momentum/momentum_bot.py",
        "cloud": "aws-target",
        "metadata": {
            "strategy": "momentum"
        }
    },
    {
        "service_id": "mean-reversion-bot",
        "service_type": "execution_node",
        "endpoint": "local-process:services/bots/mean-reversion/mean_reversion_bot.py",
        "cloud": "aws-target",
        "metadata": {
            "strategy": "mean_reversion"
        }
    },
    {
        "service_id": "fingerprint-service",
        "service_type": "intelligence_node",
        "endpoint": "local-process:services/fingerprint/fingerprint_service.py",
        "cloud": "gcp-target",
        "metadata": {
            "role": "feature_extraction"
        }
    },
    {
        "service_id": "inference-api",
        "service_type": "ml_inference_node",
        "endpoint": "http://localhost:8000",
        "cloud": "gcp-target",
        "metadata": {
            "health": "http://localhost:8000/health"
        }
    },
    {
        "service_id": "orchestrator",
        "service_type": "orchestration_node",
        "endpoint": "local-process:services/orchestrator/orchestrator.py",
        "cloud": "azure-target",
        "metadata": {
            "mode": "manual_or_auto"
        }
    },
    {
        "service_id": "dashboard",
        "service_type": "human_in_loop_node",
        "endpoint": "http://localhost:8501",
        "cloud": "azure-target",
        "metadata": {
            "health": "http://localhost:8501/health"
        }
    }
]

for svc in services:
    registered = register_service(**svc)
    print(f"Registered {registered['service_id']} as {registered['service_type']}")

print("\nRegistry written to data/registry/service_registry.json")
