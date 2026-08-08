import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from database import DatabaseManager
from event_broker import EventBrokerManager
from fastapi import FastAPI

from api.core.config import get_api_settings
from api.core.infrastructure import InfrastructureManager
from api.core.logging import configure_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Initialize API resources at startup and dispose them at shutdown.

    Args:
        app: FastAPI application receiving infrastructure state.

    Yields:
        Control to FastAPI while the application is running.
    """
    settings = get_api_settings()
    configure_logging(settings.API_LOG_LEVEL)

    infrastructure_manager = InfrastructureManager(
        DatabaseManager(settings.database_settings),
        EventBrokerManager(settings.event_broker_settings),
    )
    await infrastructure_manager.initialize()
    app.state.infrastructure_manager = infrastructure_manager

    logger.info('API infrastructure initialized.')

    try:
        yield
    finally:
        await infrastructure_manager.dispose()
        logger.info('API infrastructure disposed.')
