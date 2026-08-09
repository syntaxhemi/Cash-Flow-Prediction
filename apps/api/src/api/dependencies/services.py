from typing import Annotated

from database import IUnitOfWork
from event_broker import IEventBrokerManager
from fastapi import Depends

from api.core.config import ApiSettings, get_api_settings
from api.dependencies.database import get_unit_of_work
from api.dependencies.event_broker import get_event_broker_manager
from api.services.enterprise import EnterpriseService
from api.services.ingestion import (
    IngestionRunService,
    IngestionSourceCredentialService,
    IngestionSourceService,
)


def get_enterprise_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> EnterpriseService:
    """Build an enterprise service for the current request.

    Args:
        uow: Request-scoped database unit of work.

    Returns:
        Enterprise application service.
    """
    return EnterpriseService(uow)


def get_ingestion_source_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> IngestionSourceService:
    """Build an ingestion-source service for the current request.

    Args:
        uow: Request-scoped database unit of work.

    Returns:
        Ingestion-source application service.
    """
    return IngestionSourceService(uow)


def get_ingestion_source_credential_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> IngestionSourceCredentialService:
    """Build an ingestion-source credential service for the current request.

    Args:
        uow: Request-scoped database unit of work.

    Returns:
        Ingestion-source credential application service.
    """
    return IngestionSourceCredentialService(uow)


def get_ingestion_run_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    event_broker_manager: Annotated[
        IEventBrokerManager, Depends(get_event_broker_manager)
    ],
    settings: Annotated[ApiSettings, Depends(get_api_settings)],
) -> IngestionRunService:
    """Build an ingestion-run service for the current request.

    Args:
        uow: Request-scoped database unit of work.
        event_broker_manager: Shared Redis Streams manager.
        settings: API settings for the current runtime.

    Returns:
        Ingestion-run application service.
    """
    return IngestionRunService(
        uow,
        event_broker_manager,
        settings.INGESTION_SYNC_STREAM_NAME,
    )
