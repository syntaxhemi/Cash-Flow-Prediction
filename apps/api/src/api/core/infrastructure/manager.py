from database import IDatabaseManager


class InfrastructureManager:
    def __init__(self, database_manager: IDatabaseManager) -> None:
        """Initialize API infrastructure management.

        Args:
            database_manager: Shared database manager instance.
        """
        self._database_manager = database_manager

    async def initialize(self) -> None:
        """Initialize and verify all API infrastructure resources."""
        await self._database_manager.initialize()
        await self._database_manager.check_connection()

    def get_database_manager(self) -> IDatabaseManager:
        """Return the shared database manager."""
        return self._database_manager

    async def dispose(self) -> None:
        """Dispose all managed API infrastructure resources."""
        await self._database_manager.dispose()
