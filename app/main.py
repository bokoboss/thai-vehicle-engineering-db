from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import PROJECT_ROOT, settings
from app.web.routes import router


def create_app() -> FastAPI:
    application = FastAPI(title=settings.app_name, version="0.1.0")
    application.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "app" / "web" / "static")), name="static")
    application.include_router(router)
    return application


app = create_app()
