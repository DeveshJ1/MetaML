import json
import os
from datetime import datetime, timezone

REGISTRY_PATH = "data/registry/service_registry.json"

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def load_registry():
    if not os.path.exists(REGISTRY_PATH):
        return {}

    try:
        with open(REGISTRY_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_registry(registry):
    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)

def register_service(service_id, service_type, endpoint, cloud, status="healthy", metadata=None):
    registry = load_registry()

    registry[service_id] = {
        "service_id": service_id,
        "service_type": service_type,
        "endpoint": endpoint,
        "cloud": cloud,
        "status": status,
        "metadata": metadata or {},
        "last_heartbeat": utc_now()
    }

    save_registry(registry)
    return registry[service_id]

def heartbeat(service_id, status="healthy"):
    registry = load_registry()

    if service_id not in registry:
        return None

    registry[service_id]["status"] = status
    registry[service_id]["last_heartbeat"] = utc_now()

    save_registry(registry)
    return registry[service_id]

def list_services():
    return load_registry()

def get_service(service_id):
    return load_registry().get(service_id)
