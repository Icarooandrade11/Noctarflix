from datetime import datetime
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Noctarflix CATALOG Service", version="1.0.0")


class Title(BaseModel):
    id: str
    name: str
    category: str
    synopsis: str
    thumb: str


CATALOG: List[Title] = [
    Title(
        id="001",
        name="Planeta Rubi",
        category="Ficção Científica",
        synopsis="Exploradores descobrem um mundo coberto de cristais.",
        thumb="/assets/ruby-world.jpg",
    ),
    Title(
        id="002",
        name="Cidade Partida",
        category="Drama",
        synopsis="Famílias lutam para reconstruir seus laços após uma grande enchente.",
        thumb="/assets/split-city.jpg",
    ),
    Title(
        id="003",
        name="Rota 404",
        category="Suspense",
        synopsis="Um hacker precisa parar um ataque enquanto corre do próprio grupo.",
        thumb="/assets/route404.jpg",
    ),
]
START_TIME = datetime.utcnow()


@app.get("/recommendations", response_model=List[Title])
def recommendations():
    return CATALOG


@app.get("/title/{title_id}", response_model=Title)
def get_title(title_id: str):
    for item in CATALOG:
        if item.id == title_id:
            return item
    return CATALOG[0]


@app.get("/health")
def health():
    return {
        "service": "CATALOG",
        "uptime_seconds": int((datetime.utcnow() - START_TIME).total_seconds()),
        "titles": len(CATALOG),
    }
