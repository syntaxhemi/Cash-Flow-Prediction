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


class InvalidForecastRunError(DomainError):
    """Raised when forecast run data is invalid."""


class InvalidSimulationError(DomainError):
    """Raised when simulation data is invalid."""


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
