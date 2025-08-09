from fastapi import FastAPI
from app.api.v1 import health, candidates, stages  # добавили stages


def include_routers(app: FastAPI):
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(candidates.router, prefix="/api/v1/candidates")
    app.include_router(stages.router)  # подключили stages
