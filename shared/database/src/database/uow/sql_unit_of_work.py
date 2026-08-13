from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories import (
    CounterpartyMonthlyReceivableRepository,
    CounterpartyRepository,
    EnterpriseRepository,
    FinancialTransactionRepository,
    IngestionRunRepository,
    IngestionSourceCredentialRepository,
    IngestionSourceRepository,
    IngestionUploadRepository,
    MonthlyCashflowAggregateRepository,
    StaticFinancialSnapshotRepository,
)


class SqlAlchemyUnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        """Initialize repositories over a shared async session.

        Args:
            session: Session whose operations form one unit of work.
        """
        self._session = session
        self._counterparties = CounterpartyRepository(session)
        self._counterparty_monthly_receivables = (
            CounterpartyMonthlyReceivableRepository(session)
        )
        self._monthly_cashflow_aggregates = MonthlyCashflowAggregateRepository(session)
        self._enterprises = EnterpriseRepository(session)
        self._ingestion_sources = IngestionSourceRepository(session)
        self._ingestion_source_credentials = IngestionSourceCredentialRepository(
            session
        )
        self._ingestion_runs = IngestionRunRepository(session)
        self._financial_transactions = FinancialTransactionRepository(session)
        self._ingestion_uploads = IngestionUploadRepository(session)
        self._static_financial_snapshots = StaticFinancialSnapshotRepository(session)

    @property
    def counterparties(self) -> CounterpartyRepository:
        """Return the counterparty repository."""
        return self._counterparties

    @property
    def counterparty_monthly_receivables(
        self,
    ) -> CounterpartyMonthlyReceivableRepository:
        """Return the counterparty receivable aggregate repository."""
        return self._counterparty_monthly_receivables

    @property
    def monthly_cashflow_aggregates(self) -> MonthlyCashflowAggregateRepository:
        """Return the enterprise-month aggregate repository."""
        return self._monthly_cashflow_aggregates

    @property
    def enterprises(self) -> EnterpriseRepository:
        """Return the enterprise repository."""
        return self._enterprises

    @property
    def ingestion_sources(self) -> IngestionSourceRepository:
        """Return the ingestion-source repository."""
        return self._ingestion_sources

    @property
    def ingestion_source_credentials(self) -> IngestionSourceCredentialRepository:
        """Return the ingestion-source credential repository."""
        return self._ingestion_source_credentials

    @property
    def ingestion_runs(self) -> IngestionRunRepository:
        """Return the ingestion-run repository."""
        return self._ingestion_runs

    @property
    def financial_transactions(self) -> FinancialTransactionRepository:
        """Return the financial-transaction repository."""
        return self._financial_transactions

    @property
    def ingestion_uploads(self) -> IngestionUploadRepository:
        """Return the ingestion-upload repository."""
        return self._ingestion_uploads

    @property
    def static_financial_snapshots(self) -> StaticFinancialSnapshotRepository:
        """Return the static-financial-snapshot repository."""
        return self._static_financial_snapshots

    async def commit(self) -> None:
        """Commit all pending changes in the unit of work."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Rollback all pending changes in the unit of work."""
        await self._session.rollback()

    async def close(self) -> None:
        """Close the underlying database session."""
        await self._session.close()
