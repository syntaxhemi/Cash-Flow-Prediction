from contextlib import AbstractAsyncContextManager
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession


class ISessionManager(Protocol):
    def create_session(self) -> AsyncSession: ...

    def session_scope(self) -> AbstractAsyncContextManager[AsyncSession]: ...

    async def dispose(self) -> None: ...
