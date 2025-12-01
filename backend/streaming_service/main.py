from datetime import datetime
from typing import Dict

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Noctarflix STREAMING Service", version="1.0.0")


class PlayRequest(BaseModel):
    token: str
    title_id: str
    quality: str = "auto"


STREAM_SESSIONS: Dict[str, Dict[str, str]] = {}
START_TIME = datetime.utcnow()
MONITOR_URL = "http://monitor:5004"


async def send_metric(event: Dict[str, str]):
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.post(f"{MONITOR_URL}/heartbeat", json=event)
    except httpx.HTTPError:
        pass


@app.post("/play")
async def play(payload: PlayRequest):
    if not payload.token:
        raise HTTPException(status_code=401, detail="Token obrigatório")
    session_id = f"session-{payload.title_id}-{int(datetime.utcnow().timestamp())}"
    stream_url = f"https://cdn.streamprime.local/{payload.title_id}/master.m3u8"
    STREAM_SESSIONS[session_id] = {
        "title_id": payload.title_id,
        "quality": payload.quality,
        "started_at": datetime.utcnow().isoformat(),
    }
    await send_metric(
        {"service": "STREAMING", "instance": "S3", "timestamp": datetime.utcnow().isoformat()}
    )
    return {"session_id": session_id, "url": stream_url}


@app.get("/health")
def health():
    return {
        "service": "STREAMING",
        "uptime_seconds": int((datetime.utcnow() - START_TIME).total_seconds()),
        "sessions": len(STREAM_SESSIONS),
    }
