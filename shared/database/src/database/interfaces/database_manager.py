from typing import Protocol

from database.interfaces.session_manager import ISessionManager


class IDatabaseManager(Protocol):
    def get_session_manager(self) -> ISessionManager:
        """Return the initialized session manager."""
        ...

    async def initialize(self) -> None:
        """Initialize database connectivity."""
        ...

    async def check_connection(self) -> None:
        """Check database connectivity."""
        ...

    async def dispose(self) -> None:
        """Release database resources."""
        ...
