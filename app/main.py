"""CleanRoom Harness API.

FastAPI entry point. Routers stay thin; logic lives in services; every model
call goes through the LiteLLM gateway; the policy gate runs before anything
that touches models, data, or tools.
"""

import logging

from fastapi import FastAPI

from app.routers import chat, health, ingest, retrieve, tools
from app.settings import get_settings
from app.telemetry import setup_telemetry

logging.basicConfig(level=logging.INFO)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="CleanRoom Harness",
        version=settings.app_version,
        description=(
            "A clean-room, company-portable AI systems harness for regulated "
            "enterprise and government workflows. The architecture is portable. "
            "Implementations are not."
        ),
    )
    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(ingest.router)
    app.include_router(retrieve.router)
    app.include_router(tools.router)
    setup_telemetry(app)
    return app


app = create_app()
