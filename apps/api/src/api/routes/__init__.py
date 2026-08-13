"""API routes package."""

from fastapi import FastAPI

from api.routes.enterprises import router as enterprises_router
from api.routes.financial import router as financial_router
from api.routes.ingestion_sources import router as ingestion_sources_router


def register_routes(app: FastAPI) -> None:
    """Register workflow routers on the application.

    Args:
        app: FastAPI application receiving the routers.
    """
    app.include_router(enterprises_router)
    app.include_router(financial_router)
    app.include_router(ingestion_sources_router)
