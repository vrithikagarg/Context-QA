from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.api.main import api_router
from app.core.config import settings

from typing import Dict

app = FastAPI(
    title="Context QA",
    description="RAG-based question-answering API backed by pgvector.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/metrics")
def metrics():
    return {"message": "Metrics endpoint"}


@app.get("/")
async def root() -> Dict[str, str]:
    """An example "Hello world" FastAPI route."""
    return {"message": "Context QA API"}


app.include_router(api_router, prefix=settings.API_V1_STR)
