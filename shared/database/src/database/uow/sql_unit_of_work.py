from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories import EnterpriseRepository, IngestionSourceRepository


class SqlAlchemyUnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        """Initialize repositories over a shared async session.

        Args:
            session: Session whose operations form one unit of work.
        """
        self._session = session
        self._enterprises = EnterpriseRepository(session)
        self._ingestion_sources = IngestionSourceRepository(session)

    @property
    def enterprises(self) -> EnterpriseRepository:
        """Return the enterprise repository."""
        return self._enterprises

    @property
    def ingestion_sources(self) -> IngestionSourceRepository:
        """Return the ingestion-source repository."""
        return self._ingestion_sources

    async def commit(self) -> None:
        """Commit all pending changes in the unit of work."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Rollback all pending changes in the unit of work."""
        await self._session.rollback()

    async def close(self) -> None:
        """Close the underlying database session."""
        await self._session.close()
