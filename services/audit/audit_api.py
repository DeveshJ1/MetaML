from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any

from shared.libs.audit_chain import append_audit_event, read_chain, verify_chain

app = FastAPI(title="MetaML Tamper-Evident Audit API")

class AuditEventRequest(BaseModel):
    event_type: str
    event_payload: Dict[str, Any]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/audit")
def audit_events():
    return read_chain()

@app.get("/audit/verify")
def verify():
    return verify_chain()

@app.post("/audit")
def append_event(req: AuditEventRequest):
    return append_audit_event(
        event_type=req.event_type,
        event_payload=req.event_payload
    )
