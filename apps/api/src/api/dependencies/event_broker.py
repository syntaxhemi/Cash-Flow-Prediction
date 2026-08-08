from typing import Annotated

from event_broker import IEventBrokerManager
from fastapi import Depends

from api.core.infrastructure import InfrastructureManager
from api.dependencies.database import get_infrastructure_manager


def get_event_broker_manager(
    infrastructure_manager: Annotated[
        InfrastructureManager, Depends(get_infrastructure_manager)
    ],
) -> IEventBrokerManager:
    """Return the lifespan-managed event-broker manager.

    Args:
        infrastructure_manager: Lifespan-managed infrastructure.

    Returns:
        Shared event-broker manager.
    """
    return infrastructure_manager.get_event_broker_manager()
