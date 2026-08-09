from collections.abc import AsyncIterator
from typing import Protocol

from integrations.models import (
    CanonicalTransactionRecord,
    IngestionAdapterContext,
    RawIngestionRecord,
)


class IIngestionAdapter(Protocol):
    """Protocol implemented by source-specific ingestion adapters."""

    @property
    def source_key(self) -> str:
        """Return the stable key used to resolve this adapter."""
        ...

    async def validate_configuration(self, context: IngestionAdapterContext) -> None:
        """Validate source configuration and credentials before synchronization.

        Args:
            context: Source and synchronization configuration.
        """
        ...

    def fetch_records(
        self, context: IngestionAdapterContext
    ) -> AsyncIterator[RawIngestionRecord]:
        """Yield source records from the external accounting system.

        Args:
            context: Source and synchronization configuration.

        Yields:
            Raw records returned by the external source.
        """
        ...

    def translate_record(
        self,
        context: IngestionAdapterContext,
        record: RawIngestionRecord,
    ) -> CanonicalTransactionRecord:
        """Translate one source record into the canonical transaction shape.

        Args:
            context: Source and synchronization configuration.
            record: Raw source record to translate.

        Returns:
            Canonical transaction data independent of the source format.
        """
        ...
