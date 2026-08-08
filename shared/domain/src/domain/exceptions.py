class DomainError(Exception):
    """Base exception for domain-layer errors."""


class InvalidEnterpriseConfigurationError(DomainError):
    """Raised when enterprise configuration is invalid."""


class InvalidIngestionSourceError(DomainError):
    """Raised when an ingestion source is invalid."""


class InvalidIngestionRunError(DomainError):
    """Raised when ingestion run data is invalid."""


class InvalidFinancialRecordError(DomainError):
    """Raised when a financial record violates a domain invariant."""


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
