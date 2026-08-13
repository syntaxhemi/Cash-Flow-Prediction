from dataclasses import dataclass

from domain.exceptions import (
    DomainError,
    EnterpriseAlreadyExistsError,
    EnterpriseNotFoundError,
    IngestionRunNotFoundError,
    IngestionSourceAlreadyExistsError,
    IngestionSourceCredentialNotFoundError,
    IngestionSourceNotFoundError,
    InvalidEnterpriseConfigurationError,
    InvalidFinancialRecordError,
    InvalidForecastRunError,
    InvalidIngestionRunError,
    InvalidIngestionSourceCredentialStateError,
    InvalidIngestionSourceError,
    InvalidSimulationError,
    StaticFinancialSnapshotAlreadyExistsError,
    StaticFinancialSnapshotNotFoundError,
)


@dataclass(frozen=True, slots=True)
class DomainErrorMapping:
    """HTTP representation of a domain exception."""

    status_code: int
    error_code: str


def get_domain_error_mapping(error: DomainError) -> DomainErrorMapping:
    """Map a domain exception to an HTTP response description.

    Args:
        error: Domain exception raised by application logic.

    Returns:
        HTTP status and stable error code.
    """
    if isinstance(
        error,
        (
            EnterpriseAlreadyExistsError,
            IngestionSourceAlreadyExistsError,
            StaticFinancialSnapshotAlreadyExistsError,
        ),
    ):
        return DomainErrorMapping(409, 'resource_already_exists')
    if isinstance(
        error,
        (
            EnterpriseNotFoundError,
            IngestionSourceNotFoundError,
            IngestionSourceCredentialNotFoundError,
            IngestionRunNotFoundError,
            StaticFinancialSnapshotNotFoundError,
        ),
    ):
        return DomainErrorMapping(404, 'resource_not_found')
    if isinstance(
        error,
        (
            InvalidEnterpriseConfigurationError,
            InvalidFinancialRecordError,
            InvalidForecastRunError,
            InvalidIngestionRunError,
            InvalidIngestionSourceError,
            InvalidIngestionSourceCredentialStateError,
            InvalidSimulationError,
        ),
    ):
        return DomainErrorMapping(400, 'domain_validation_error')
    return DomainErrorMapping(400, 'domain_error')
