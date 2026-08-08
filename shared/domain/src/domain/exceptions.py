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
