from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any

from shared.libs.service_registry import (
    register_service,
    heartbeat,
    list_services,
    get_service
)

app = FastAPI(title="MetaML Decentralized Service Registry")

class RegisterRequest(BaseModel):
    service_id: str
    service_type: str
    endpoint: str
    cloud: str
    status: str = "healthy"
    metadata: Dict[str, Any] = {}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/services")
def services():
    return list_services()

@app.get("/services/{service_id}")
def service(service_id: str):
    svc = get_service(service_id)
    if svc is None:
        return {"error": "service not found"}
    return svc

@app.post("/register")
def register(req: RegisterRequest):
    return register_service(
        service_id=req.service_id,
        service_type=req.service_type,
        endpoint=req.endpoint,
        cloud=req.cloud,
        status=req.status,
        metadata=req.metadata
    )

@app.post("/heartbeat/{service_id}")
def service_heartbeat(service_id: str):
    svc = heartbeat(service_id)
    if svc is None:
        return {"error": "service not found"}
    return svc
