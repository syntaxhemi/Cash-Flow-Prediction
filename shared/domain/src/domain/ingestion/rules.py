from datetime import datetime
from typing import Protocol

from domain.exceptions import InvalidIngestionRunError, InvalidIngestionSourceError


class IIngestionRules(Protocol):
    def validate_source(self, source_key: str, display_name: str) -> None:
        """Validate ingestion source identity fields."""
        ...

    def validate_run(
        self,
        *,
        records_received: int,
        records_processed: int,
        records_failed: int,
        started_at: datetime | None,
        finished_at: datetime | None,
    ) -> None:
        """Validate ingestion counts and lifecycle timestamps."""
        ...


class DefaultIngestionRules:
    def validate_source(self, source_key: str, display_name: str) -> None:
        """Validate source key and display name.

        Args:
            source_key: Registry lookup key.
            display_name: Human-readable source name.

        Raises:
            InvalidIngestionSourceError: If either value is empty.
        """
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
        """Validate ingestion record counts and lifecycle timestamps.

        Args:
            records_received: Number of records received.
            records_processed: Number of successfully processed records.
            records_failed: Number of failed records.
            started_at: Run start timestamp.
            finished_at: Run finish timestamp.

        Raises:
            InvalidIngestionRunError: If counts or timestamps are inconsistent.
        """
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
