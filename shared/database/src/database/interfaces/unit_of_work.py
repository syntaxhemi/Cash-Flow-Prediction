from typing import Protocol

from database.repositories import (
    CounterpartyRepository,
    EnterpriseRepository,
    FinancialTransactionRepository,
    IngestionRunRepository,
    IngestionSourceCredentialRepository,
    IngestionSourceRepository,
    IngestionUploadRepository,
)


class IUnitOfWork(Protocol):
    @property
    def counterparties(self) -> CounterpartyRepository:
        """Return the counterparty repository."""
        ...

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

    @property
    def ingestion_runs(self) -> IngestionRunRepository:
        """Return the ingestion-run repository."""
        ...

    @property
    def financial_transactions(self) -> FinancialTransactionRepository:
        """Return the financial-transaction repository."""
        ...

    @property
    def ingestion_uploads(self) -> IngestionUploadRepository:
        """Return the ingestion-upload repository."""
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
