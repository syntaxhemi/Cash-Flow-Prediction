class DomainError(Exception):
    """Base exception for domain-layer errors."""


class InvalidEnterpriseConfigurationError(DomainError):
    """Raised when enterprise configuration is invalid."""


class InvalidIngestionSourceError(DomainError):
    """Raised when an ingestion source is invalid."""


class InvalidIngestionRunError(DomainError):
    """Raised when ingestion run data is invalid."""


class IngestionRunNotFoundError(DomainError):
    """Raised when an ingestion run cannot be found."""


class IngestionUploadNotFoundError(DomainError):
    """Raised when an ingestion upload cannot be found."""


class IngestionUploadAlreadyExistsError(DomainError):
    """Raised when an ingestion run already has upload metadata."""


class InvalidFinancialRecordError(DomainError):
    """Raised when a financial record violates a domain invariant."""


class FinancialTransactionNotFoundError(DomainError):
    """Raised when a financial transaction cannot be found."""


class CounterpartyNotFoundError(DomainError):
    """Raised when a counterparty cannot be found."""


class CounterpartyAlreadyExistsError(DomainError):
    """Raised when an enterprise already has a counterparty with the key."""


class FinancialTransactionAlreadyExistsError(DomainError):
    """Raised when a source transaction has already been persisted."""


class StaticFinancialSnapshotNotFoundError(DomainError):
    """Raised when a static financial snapshot cannot be found."""


class StaticFinancialSnapshotAlreadyExistsError(DomainError):
    """Raised when an enterprise already has a snapshot for a date."""


class MonthlyCashflowAggregateNotFoundError(DomainError):
    """Raised when a monthly cash-flow aggregate cannot be found."""


class MonthlyCashflowAggregateAlreadyExistsError(DomainError):
    """Raised when an enterprise already has an aggregate for a period."""


class CounterpartyMonthlyReceivableNotFoundError(DomainError):
    """Raised when a counterparty receivable aggregate cannot be found."""


class CounterpartyMonthlyReceivableAlreadyExistsError(DomainError):
    """Raised when a counterparty already has a receivable aggregate for a period."""


class InvalidForecastRunError(DomainError):
    """Raised when forecast run data is invalid."""


class InvalidSimulationError(DomainError):
    """Raised when simulation data is invalid."""


class SimulationRunNotFoundError(DomainError):
    """Raised when a simulation run cannot be found."""


class SimulationRunHasChildrenError(DomainError):
    """Raised when a simulation run cannot be deleted while outputs exist."""


class SimulationScenarioNotFoundError(DomainError):
    """Raised when a simulation scenario cannot be found."""


class ReceivablesRankingNotFoundError(DomainError):
    """Raised when a receivables ranking cannot be found."""


class MitigationRecommendationNotFoundError(DomainError):
    """Raised when a mitigation recommendation cannot be found."""


class EnterpriseAlreadyExistsError(DomainError):
    """Raised when an enterprise external key already exists."""


class EnterpriseNotFoundError(DomainError):
    """Raised when an enterprise cannot be found."""


class IngestionSourceAlreadyExistsError(DomainError):
    """Raised when an enterprise source key already exists."""


class IngestionSourceNotFoundError(DomainError):
    """Raised when an ingestion source cannot be found."""


class IngestionSourceCredentialNotFoundError(DomainError):
    """Raised when an ingestion-source credential cannot be found."""


class InvalidIngestionSourceCredentialStateError(DomainError):
    """Raised when an ingestion-source credential lifecycle transition is invalid."""


class IntegrationAdapterNotFoundError(DomainError):
    """Raised when no integration adapter is registered for a source key."""


class IntegrationAdapterAlreadyRegisteredError(DomainError):
    """Raised when an integration adapter key is registered more than once."""
