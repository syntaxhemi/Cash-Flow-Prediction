from datetime import datetime
from typing import Protocol

from domain.exceptions import InvalidIngestionRunError, InvalidIngestionSourceError


class IIngestionRules(Protocol):
    def validate_source(self, source_key: str, display_name: str) -> None: ...

    def validate_run(
        self,
        *,
        records_received: int,
        records_processed: int,
        records_failed: int,
        started_at: datetime | None,
        finished_at: datetime | None,
    ) -> None: ...


class DefaultIngestionRules:
    def validate_source(self, source_key: str, display_name: str) -> None:
        if not source_key.strip():
            raise InvalidIngestionSourceError('Source key must not be empty.')
        if not display_name.strip():
            raise InvalidIngestionSourceError('Source display name must not be empty.')

    def validate_run(
        self,
        *,
        records_received: int,
        records_processed: int,
        records_failed: int,
        started_at: datetime | None,
        finished_at: datetime | None,
    ) -> None:
        counts = (records_received, records_processed, records_failed)
        if any(count < 0 for count in counts):
            raise InvalidIngestionRunError(
                'Ingestion record counts must be non-negative.'
            )
        if records_processed + records_failed > records_received:
            raise InvalidIngestionRunError(
                'Processed and failed records cannot exceed received records.'
            )
        if (
            started_at is not None
            and finished_at is not None
            and finished_at < started_at
        ):
            raise InvalidIngestionRunError(
                'Ingestion runs cannot finish before they start.'
            )
