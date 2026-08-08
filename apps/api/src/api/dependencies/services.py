from typing import Annotated

from database import IUnitOfWork
from fastapi import Depends

from api.dependencies.database import get_unit_of_work
from api.services.enterprise import EnterpriseService
from api.services.ingestion import IngestionSourceService


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
