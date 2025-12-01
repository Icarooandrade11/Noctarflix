from datetime import datetime
from typing import Dict

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Noctarflix MONITOR/DISCOVERY Service", version="1.0.0")


class Heartbeat(BaseModel):
    service: str
    instance: str
    timestamp: datetime


REGISTRY: Dict[str, Dict[str, str]] = {
    "auth.streamprime.local": {"primary": "http://auth:5000", "backup": "http://notify:5005"},
    "catalog.streamprime.local": {"primary": "http://catalog:5001", "backup": "http://auth:5000"},
    "streaming.streamprime.local": {"primary": "http://streaming:5002", "backup": "http://catalog:5001"},
    "billing.streamprime.local": {"primary": "http://billing:5003", "backup": "http://streaming:5002"},
    "monitor.streamprime.local": {"primary": "http://monitor:5004", "backup": "http://billing:5003"},
    "notify.streamprime.local": {"primary": "http://notify:5005", "backup": "http://monitor:5004"},
}
HEARTBEATS: Dict[str, Heartbeat] = {}
START_TIME = datetime.utcnow()


@app.post("/heartbeat")
def heartbeat(payload: Heartbeat):
    HEARTBEATS[payload.service] = payload
    return {"status": "ok"}


@app.get("/status")
def status():
    return {"active": list(HEARTBEATS.keys())}


@app.get("/resolve")
def resolve(name: str):
    entry = REGISTRY.get(name)
    if not entry:
        return {"error": "nome não encontrado"}
    return entry


@app.get("/health")
def health():
    return {
        "service": "MONITOR/DISCOVERY",
        "uptime_seconds": int((datetime.utcnow() - START_TIME).total_seconds()),
        "registered": len(HEARTBEATS),
    }
