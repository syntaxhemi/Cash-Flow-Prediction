import asyncio
import logging

from database import DatabaseManager
from event_broker import EventBrokerManager
from integrations import (
    CSVFileAdapter,
    ERPNextAdapter,
    ExcelFileAdapter,
    IngestionAdapterRegistry,
)

from worker.core.config import get_worker_settings
from worker.core.logging import configure_logging
from worker.jobs import run_ingestion_consumer

logger = logging.getLogger(__name__)


async def run() -> None:
    """Initialize worker infrastructure and run the ingestion consumer."""
    settings = get_worker_settings()
    configure_logging(settings.WORKER_LOG_LEVEL)
    database_manager = DatabaseManager(settings.database_settings)
    event_broker_manager = EventBrokerManager(settings.event_broker_settings)

    registry = IngestionAdapterRegistry(
        {
            'erpnext': ERPNextAdapter(),
            'csv': CSVFileAdapter(),
            'excel': ExcelFileAdapter(),
        }
    )

    await database_manager.initialize()
    await database_manager.check_connection()
    await event_broker_manager.initialize()
    await event_broker_manager.check_connection()
    logger.info('Worker infrastructure initialized.')

    try:
        await run_ingestion_consumer(
            settings, database_manager, event_broker_manager, registry
        )
    finally:
        await event_broker_manager.dispose()
        await database_manager.dispose()
        logger.info('Worker infrastructure disposed.')


def main() -> None:
    """Run the background worker process."""
    asyncio.run(run())


if __name__ == '__main__':
    main()
