from typing import Protocol

from database.repositories import (
    CounterpartyMonthlyReceivableRepository,
    CounterpartyRepository,
    EnterpriseRepository,
    FinancialTransactionRepository,
    ForecastRepository,
    IngestionRunRepository,
    IngestionSourceCredentialRepository,
    IngestionSourceRepository,
    IngestionUploadRepository,
    MitigationRecommendationRepository,
    MonthlyCashflowAggregateRepository,
    ReceivablesRankingRepository,
    SimulationRunRepository,
    SimulationScenarioRepository,
    StaticFinancialSnapshotRepository,
)


class IUnitOfWork(Protocol):
    @property
    def counterparties(self) -> CounterpartyRepository:
        """Return the counterparty repository."""
        ...

    @property
    def counterparty_monthly_receivables(
        self,
    ) -> CounterpartyMonthlyReceivableRepository:
        """Return the counterparty receivable aggregate repository."""
        ...

    @property
    def monthly_cashflow_aggregates(self) -> MonthlyCashflowAggregateRepository:
        """Return the enterprise-month aggregate repository."""
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
    def forecasts(self) -> ForecastRepository:
        """Return the forecast persistence repository."""
        ...

    @property
    def ingestion_uploads(self) -> IngestionUploadRepository:
        """Return the ingestion-upload repository."""
        ...

    @property
    def static_financial_snapshots(self) -> StaticFinancialSnapshotRepository:
        """Return the static-financial-snapshot repository."""
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

    @property
    def simulation_runs(self) -> SimulationRunRepository:
        """Return the simulation-run repository."""
        ...

    @property
    def simulation_scenarios(self) -> SimulationScenarioRepository:
        """Return the simulation-scenario repository."""
        ...

    @property
    def receivables_rankings(self) -> ReceivablesRankingRepository:
        """Return the receivables-ranking repository."""
        ...

    @property
    def mitigation_recommendations(self) -> MitigationRecommendationRepository:
        """Return the mitigation-recommendation repository."""
        ...
