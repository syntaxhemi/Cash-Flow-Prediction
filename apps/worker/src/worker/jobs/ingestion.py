import logging
from collections.abc import Mapping

from database import DatabaseManager, SqlAlchemyUnitOfWork
from domain.exceptions import DomainError
from event_broker import IEventBrokerManager
from integrations import IngestionAdapterRegistry
from integrations.exceptions import IntegrationAdapterError
from sqlalchemy.exc import SQLAlchemyError

from worker.core.config import WorkerSettings
from worker.services.ingestion import IngestionSynchronizationService

logger = logging.getLogger(__name__)


async def run_ingestion_consumer(
    settings: WorkerSettings,
    database_manager: DatabaseManager,
    event_broker_manager: IEventBrokerManager,
    registry: IngestionAdapterRegistry,
) -> None:
    """Consume and execute ingestion synchronization commands.

    Args:
        settings: Worker runtime settings.
        database_manager: Initialized database manager.
        event_broker_manager: Initialized Redis Streams manager.
        registry: Source adapter registry.
    """
    await event_broker_manager.create_consumer_group(
        settings.INGESTION_SYNC_STREAM_NAME,
        settings.WORKER_CONSUMER_GROUP,
        start_id='0',
        mkstream=True,
    )
    while True:
        batches = await event_broker_manager.read_group(
            settings.WORKER_CONSUMER_GROUP,
            settings.WORKER_CONSUMER_NAME,
            {settings.INGESTION_SYNC_STREAM_NAME: '>'},
            count=settings.WORKER_BATCH_SIZE,
            block_ms=settings.WORKER_BLOCK_MS,
        )
        for stream_name, messages in batches:
            for message_id, fields in messages:
                await _process_message(
                    stream_name,
                    message_id,
                    fields,
                    database_manager,
                    event_broker_manager,
                    settings,
                    registry,
                )


async def _process_message(
    stream_name: str,
    message_id: str,
    fields: Mapping[str, str],
    database_manager: DatabaseManager,
    event_broker_manager: IEventBrokerManager,
    settings: WorkerSettings,
    registry: IngestionAdapterRegistry,
) -> None:
    """Execute one synchronization command and acknowledge it."""
    session = None
    try:
        session = database_manager.get_session_manager().create_session()
        service = IngestionSynchronizationService(
            SqlAlchemyUnitOfWork(session), registry
        )
        await service.execute(dict(fields))
    except (
        DomainError,
        IntegrationAdapterError,
        KeyError,
        SQLAlchemyError,
        ValueError,
    ):
        logger.exception('Ingestion synchronization message failed: %s', message_id)
    else:
        await event_broker_manager.acknowledge(
            stream_name, settings.WORKER_CONSUMER_GROUP, [message_id]
        )
    finally:
        if session is not None:
            await session.close()
