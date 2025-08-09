from fastapi import FastAPI
from app.routers import include_routers


def create_app() -> FastAPI:
    app = FastAPI(title="HostFlow API", version="0.1.0")
    include_routers(app)
    return app


app = create_app()
