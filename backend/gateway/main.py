import os
from datetime import datetime, timedelta

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

AUTH_URL = os.getenv("AUTH_URL", "http://auth:5000")
CATALOG_URL = os.getenv("CATALOG_URL", "http://catalog:5001")
STREAMING_URL = os.getenv("STREAMING_URL", "http://streaming:5002")
BILLING_URL = os.getenv("BILLING_URL", "http://billing:5003")
NOTIFY_URL = os.getenv("NOTIFY_URL", "http://notify:5005")

app = FastAPI(title="Noctarflix API Gateway", version="1.0.0")


class Credentials(BaseModel):
    email: str
    password: str


class SubscribeRequest(BaseModel):
    email: str
    plan: str = "premium"


class PlayRequest(BaseModel):
    token: str
    title_id: str


async def _client():
    return httpx.AsyncClient(timeout=5.0)


@app.post("/register")
async def register(payload: Credentials):
    async with await _client() as client:
        response = await client.post(f"{AUTH_URL}/register", json=payload.model_dump())
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()


@app.post("/login")
async def login(payload: Credentials):
    async with await _client() as client:
        response = await client.post(f"{AUTH_URL}/login", json=payload.model_dump())
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()


@app.post("/subscribe")
async def subscribe(payload: SubscribeRequest):
    async with await _client() as client:
        sub = {
            "email": payload.email,
            "plan": payload.plan,
            "status": "active",
            "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        }
        response = await client.post(f"{BILLING_URL}/subscribe", json=sub)
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        await client.post(
            f"{NOTIFY_URL}/send",
            json={"email": payload.email, "type": "billing", "message": "Assinatura ativada"},
        )
        return response.json()


@app.get("/catalog")
async def catalog():
    async with await _client() as client:
        response = await client.get(f"{CATALOG_URL}/recommendations")
        response.raise_for_status()
        return response.json()


@app.post("/play")
async def play(payload: PlayRequest):
    async with await _client() as client:
        validate = await client.get(f"{AUTH_URL}/validate", params={"token": payload.token})
        if validate.status_code >= 400:
            raise HTTPException(status_code=401, detail="Token inválido ou expirado")
        email = validate.json().get("email")

        billing = await client.get(f"{BILLING_URL}/status", params={"email": email})
        if billing.status_code >= 400:
            raise HTTPException(status_code=402, detail="Assinatura inativa")

        play_response = await client.post(
            f"{STREAMING_URL}/play",
            json={"token": payload.token, "title_id": payload.title_id},
        )
        play_response.raise_for_status()
        return play_response.json()


@app.get("/health")
async def health():
    return {"service": "GATEWAY", "status": "ok"}
