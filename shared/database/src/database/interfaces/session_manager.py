from contextlib import AbstractAsyncContextManager
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession


class ISessionManager(Protocol):
    def create_session(self) -> AsyncSession:
        """Create an async database session."""
        ...

    def session_scope(self) -> AbstractAsyncContextManager[AsyncSession]:
        """Return a transactional session context manager."""
        ...

    async def dispose(self) -> None:
        """Release session manager resources."""
        ...
