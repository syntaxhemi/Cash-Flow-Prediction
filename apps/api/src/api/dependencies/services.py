from typing import Annotated

from database import IUnitOfWork
from event_broker import IEventBrokerManager
from fastapi import Depends

from api.core.config import ApiSettings, get_api_settings
from api.dependencies.database import get_unit_of_work
from api.dependencies.event_broker import get_event_broker_manager
from api.services.enterprise import EnterpriseService
from api.services.financial import StaticFinancialSnapshotService
from api.services.forecasting import (
    BaselineForecastService,
    HealthDeltaSimulationService,
)
from api.services.ingestion import (
    IngestionRunService,
    IngestionSourceCredentialService,
    IngestionSourceService,
    UploadStagingService,
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


def get_static_financial_snapshot_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> StaticFinancialSnapshotService:
    """Build the static-financial-snapshot application service.

    Args:
        uow: Request-scoped database unit of work.

    Returns:
        Static financial snapshot application service.
    """
    return StaticFinancialSnapshotService(uow)


def get_baseline_forecast_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    settings: Annotated[ApiSettings, Depends(get_api_settings)],
) -> BaselineForecastService:
    """Build the baseline forecasting application service.

    Args:
        uow: Request-scoped database unit of work.
        settings: API settings containing the artifact directory.

    Returns:
        Baseline forecasting application service.
    """
    return BaselineForecastService(uow, settings.FORECAST_ARTIFACT_DIRECTORY)


def get_health_delta_simulation_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    settings: Annotated[ApiSettings, Depends(get_api_settings)],
) -> HealthDeltaSimulationService:
    """Build the health delta simulation application service.

    Args:
        uow: Request-scoped database unit of work.
        settings: API settings containing the artifact directory.

    Returns:
        Health delta simulation application service.
    """
    return HealthDeltaSimulationService(uow, settings.FORECAST_ARTIFACT_DIRECTORY)


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


def get_upload_staging_service(
    settings: Annotated[ApiSettings, Depends(get_api_settings)],
) -> UploadStagingService:
    """Build the shared upload staging service.

    Args:
        settings: API settings containing upload limits and directory.

    Returns:
        Upload staging application service.
    """
    return UploadStagingService(
        settings.INGESTION_UPLOAD_DIRECTORY,
        settings.INGESTION_UPLOAD_MAX_BYTES,
    )


def get_ingestion_run_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    event_broker_manager: Annotated[
        IEventBrokerManager, Depends(get_event_broker_manager)
    ],
    settings: Annotated[ApiSettings, Depends(get_api_settings)],
    upload_staging_service: Annotated[
        UploadStagingService, Depends(get_upload_staging_service)
    ],
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
        upload_staging_service,
    )
