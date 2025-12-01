from datetime import datetime, timedelta
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

app = FastAPI(title="Noctarflix AUTH Service", version="1.0.0")


class Credentials(BaseModel):
    email: EmailStr
    password: str
    profile: str | None = None


class TokenResponse(BaseModel):
    token: str
    expires_at: datetime


auth_store: Dict[str, Dict[str, str]] = {}
token_store: Dict[str, Dict[str, str]] = {}
START_TIME = datetime.utcnow()
TOKEN_TTL_MINUTES = 60


def _generate_token(email: str) -> TokenResponse:
    token = f"token-{email}-{int(datetime.utcnow().timestamp())}"
    expires_at = datetime.utcnow() + timedelta(minutes=TOKEN_TTL_MINUTES)
    token_store[token] = {"email": email, "expires_at": expires_at.isoformat()}
    return TokenResponse(token=token, expires_at=expires_at)


@app.post("/register", response_model=TokenResponse)
def register(payload: Credentials):
    if payload.email in auth_store:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    auth_store[payload.email] = {
        "password": payload.password,
        "profile": payload.profile or "default",
    }
    return _generate_token(payload.email)


@app.post("/login", response_model=TokenResponse)
def login(payload: Credentials):
    user = auth_store.get(payload.email)
    if not user or user.get("password") != payload.password:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return _generate_token(payload.email)


@app.get("/validate")
def validate(token: str):
    data: Optional[Dict[str, str]] = token_store.get(token)
    if not data:
        raise HTTPException(status_code=401, detail="Token inválido")
    expires_at = datetime.fromisoformat(data["expires_at"])
    if expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Token expirado")
    return {"email": data["email"], "expires_at": expires_at.isoformat()}


@app.get("/health")
def health():
    return {
        "service": "AUTH",
        "uptime_seconds": int((datetime.utcnow() - START_TIME).total_seconds()),
        "users": len(auth_store),
    }
