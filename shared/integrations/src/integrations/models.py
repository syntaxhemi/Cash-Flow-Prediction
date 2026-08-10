from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from domain.enterprise import CounterpartyType
from domain.financial import TransactionDirection, TransactionStatus, TransactionType


@dataclass(frozen=True, slots=True)
class IngestionAdapterContext:
    """Describe the source and synchronization context for an adapter call."""

    enterprise_id: UUID
    ingestion_source_id: UUID
    ingestion_run_id: UUID
    configuration: Mapping[str, Any]
    secret_ref: str
    cursor: datetime | None = None
    file_path: str | None = None
    file_format: str | None = None
    file_sha256: str | None = None
    sheet_name: str | None = None


@dataclass(frozen=True, slots=True)
class RawIngestionRecord:
    """Represent one source record before canonical translation."""

    source_record_id: str
    payload: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class CanonicalTransactionRecord:
    """Represent one adapter-neutral financial transaction."""

    source_record_id: str
    transaction_type: TransactionType
    transaction_date: date
    amount: Decimal
    currency_code: str
    direction: TransactionDirection
    status: TransactionStatus
    due_date: date | None = None
    settlement_date: date | None = None
    counterparty_external_key: str | None = None
    counterparty_name: str | None = None
    counterparty_type: CounterpartyType | None = None
    reference_number: str | None = None
    description: str | None = None
    source_payload_hash: str | None = None
