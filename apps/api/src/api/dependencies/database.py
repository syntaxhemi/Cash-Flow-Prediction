from collections.abc import AsyncGenerator
from typing import Annotated

from database import IDatabaseManager, IUnitOfWork, SqlAlchemyUnitOfWork
from fastapi import Depends, Request

from api.core.infrastructure import InfrastructureManager


def get_infrastructure_manager(request: Request) -> InfrastructureManager:
    """Return the lifespan-managed infrastructure manager.

    Args:
        request: Current FastAPI request.

    Returns:
        Application infrastructure manager.
    """
    return request.app.state.infrastructure_manager


def get_database_manager(
    infrastructure_manager: Annotated[
        InfrastructureManager, Depends(get_infrastructure_manager)
    ],
) -> IDatabaseManager:
    """Return the shared database manager.

    Args:
        infrastructure_manager: Lifespan-managed infrastructure.

    Returns:
        Shared database manager.
    """
    return infrastructure_manager.get_database_manager()


async def get_unit_of_work(
    database_manager: Annotated[IDatabaseManager, Depends(get_database_manager)],
) -> AsyncGenerator[IUnitOfWork]:
    """Yield a request-scoped unit of work and rollback failures.

    Args:
        database_manager: Shared database manager dependency.

    Yields:
        Unit of work backed by a request-scoped async session.
    """
    session_manager = database_manager.get_session_manager()
    uow = SqlAlchemyUnitOfWork(session_manager.create_session())
    try:
        yield uow
    except Exception:
        await uow.rollback()
        raise
    finally:
        await uow.close()
