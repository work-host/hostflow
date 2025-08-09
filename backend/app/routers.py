from fastapi import FastAPI
from app.api.v1 import health, candidates


def include_routers(app: FastAPI):
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(candidates.router, prefix="/api/v1/candidates")
