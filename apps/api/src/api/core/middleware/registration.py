from fastapi import FastAPI

from api.core.config import ApiSettings
from api.core.middleware.cors import add_cors_middleware
from api.core.middleware.request_context import add_request_context_middleware


def register_middlewares(app: FastAPI, settings: ApiSettings) -> None:
    """Register the API middleware stack.

    Args:
        app: FastAPI application receiving middleware.
        settings: API middleware configuration.
    """
    add_cors_middleware(app, settings)
    add_request_context_middleware(app)
