from database import IDatabaseManager
from event_broker import IEventBrokerManager


class InfrastructureManager:
    def __init__(
        self,
        database_manager: IDatabaseManager,
        event_broker_manager: IEventBrokerManager,
    ) -> None:
        """Initialize API infrastructure management.

        Args:
            database_manager: Shared database manager instance.
            event_broker_manager: Shared event-broker manager instance.
        """
        self._database_manager = database_manager
        self._event_broker_manager = event_broker_manager

    async def initialize(self) -> None:
        """Initialize and verify all API infrastructure resources."""
        await self._database_manager.initialize()
        await self._database_manager.check_connection()
        await self._event_broker_manager.initialize()
        await self._event_broker_manager.check_connection()

    def get_database_manager(self) -> IDatabaseManager:
        """Return the shared database manager."""
        return self._database_manager

    def get_event_broker_manager(self) -> IEventBrokerManager:
        """Return the shared event-broker manager."""
        return self._event_broker_manager

    async def dispose(self) -> None:
        """Dispose all managed API infrastructure resources."""
        await self._event_broker_manager.dispose()
        await self._database_manager.dispose()
