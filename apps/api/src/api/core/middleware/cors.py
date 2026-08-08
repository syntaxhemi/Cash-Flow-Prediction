from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import ApiSettings


def add_cors_middleware(app: FastAPI, settings: ApiSettings) -> None:
    """Register configured CORS behavior.

    Args:
        app: FastAPI application receiving the middleware.
        settings: API settings containing CORS options.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.API_CORS_ALLOW_ORIGINS,
        allow_credentials=settings.API_CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.API_CORS_ALLOW_METHODS,
        allow_headers=settings.API_CORS_ALLOW_HEADERS,
    )
