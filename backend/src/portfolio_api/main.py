"""Portfolio Polyglotte — application FastAPI."""

import os
import certifi

os.environ.setdefault("SSL_CERT_FILE", certifi.where())
os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from portfolio_api.core.config import get_settings
from portfolio_api.db.mongo import close_mongo
from portfolio_api.db.neo4j import close_neo4j
from portfolio_api.models import HealthResponse
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_mongo()
    await close_neo4j()


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="API d'équipe du Portfolio Polyglotte — voir API_ROUTES.md",
    lifespan=lifespan,
)
logging.info("CORS origins: " + ", ".join(settings.cors_origin_list))
logging.info(settings.app_name + " is running in debug mode: " + str(settings.debug))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse, tags=["santé"])
async def health() -> HealthResponse:
    return HealthResponse()

from portfolio_api.api.personne import router as personne_router
from portfolio_api.api.competences import router as competences_router
from portfolio_api.api.projet import router as projet_router

app.include_router(competences_router, prefix="/api")  
app.include_router(personne_router, prefix="/api")
app.include_router(projet_router, prefix="/api")
# TODO (équipe) : enregistrer vos routeurs
# from portfolio_api.api.routes_candidats import router as candidats_router
# app.include_router(candidats_router, prefix="/api")
