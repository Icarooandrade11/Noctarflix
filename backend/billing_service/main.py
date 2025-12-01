from datetime import datetime
from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Noctarflix BILLING Service", version="1.0.0")


class Subscription(BaseModel):
    email: str
    plan: str
    status: str
    valid_until: datetime


subscriptions: Dict[str, Subscription] = {}
START_TIME = datetime.utcnow()


@app.post("/subscribe", response_model=Subscription)
def subscribe(payload: Subscription):
    subscriptions[payload.email] = payload
    return payload


@app.get("/status", response_model=Subscription)
def status(email: str):
    sub = subscriptions.get(email)
    if not sub:
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")
    return sub


@app.get("/health")
def health():
    return {
        "service": "BILLING",
        "uptime_seconds": int((datetime.utcnow() - START_TIME).total_seconds()),
        "subscriptions": len(subscriptions),
    }
