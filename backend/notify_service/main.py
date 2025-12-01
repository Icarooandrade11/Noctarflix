from datetime import datetime
from typing import Dict

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Noctarflix NOTIFY Service", version="1.0.0")


class Notification(BaseModel):
    email: str
    type: str
    message: str


NOTIFICATIONS: Dict[str, Notification] = {}
START_TIME = datetime.utcnow()


@app.post("/send")
def send(payload: Notification):
    NOTIFICATIONS[payload.email] = payload
    return {"status": "queued", "email": payload.email}


@app.get("/health")
def health():
    return {
        "service": "NOTIFY",
        "uptime_seconds": int((datetime.utcnow() - START_TIME).total_seconds()),
        "notifications": len(NOTIFICATIONS),
    }
