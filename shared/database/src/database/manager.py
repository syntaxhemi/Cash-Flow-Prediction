from sqlalchemy import text

from database.config import DatabaseSettings
from database.interfaces import ISessionManager
from database.session import (
    AsyncDatabaseConfig,
    SessionManager,
    create_database_engine,
    create_session_factory,
)


class DatabaseManager:
    def __init__(self, settings: DatabaseSettings) -> None:
        """Initialize a database manager.

        Args:
            settings: Database connection and pool settings.
        """
        self._settings = settings
        self._session_manager: ISessionManager | None = None

    async def initialize(self) -> None:
        """Create the engine, session factory, and session manager."""
        if self._session_manager is not None:
            return

        config = AsyncDatabaseConfig.from_settings(self._settings)
        engine = create_database_engine(config)
        session_factory = create_session_factory(engine)
        self._session_manager = SessionManager(
            engine=engine,
            session_factory=session_factory,
        )

    async def check_connection(self) -> None:
        """Verify that the configured database connection is usable."""
        session_manager = self.get_session_manager()
        async with session_manager.session_scope() as session:
            await session.execute(text('SELECT 1'))

    def get_session_manager(self) -> ISessionManager:
        """Return the initialized session manager.

        Returns:
            The shared session manager.

        Raises:
            RuntimeError: If initialization has not completed.
        """
        if self._session_manager is None:
            raise RuntimeError('Database manager has not been initialized.')

        return self._session_manager

    async def dispose(self) -> None:
        """Dispose the session manager and database engine."""
        if self._session_manager is None:
            return

        await self._session_manager.dispose()
        self._session_manager = None
