class IntegrationAdapterError(Exception):
    """Base error raised by an ingestion adapter."""


class IntegrationConfigurationError(IntegrationAdapterError):
    """Raised when adapter configuration or credentials are invalid."""


class IntegrationTransportError(IntegrationAdapterError):
    """Raised when an adapter cannot communicate with its external source."""


class IntegrationRecordTranslationError(IntegrationAdapterError):
    """Raised when an external record cannot be normalized."""
