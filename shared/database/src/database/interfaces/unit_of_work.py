from typing import Protocol

from database.repositories import (
    EnterpriseRepository,
    IngestionSourceCredentialRepository,
    IngestionSourceRepository,
)


class IUnitOfWork(Protocol):
    @property
    def enterprises(self) -> EnterpriseRepository:
        """Return the enterprise repository."""
        ...

    @property
    def ingestion_sources(self) -> IngestionSourceRepository:
        """Return the ingestion-source repository."""
        ...

    @property
    def ingestion_source_credentials(self) -> IngestionSourceCredentialRepository:
        """Return the ingestion-source credential repository."""
        ...

    async def commit(self) -> None:
        """Commit the current transaction."""
        ...

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        ...

    async def close(self) -> None:
        """Close the underlying session."""
        ...
