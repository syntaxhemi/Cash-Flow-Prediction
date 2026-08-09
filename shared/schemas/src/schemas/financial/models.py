from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from domain.enterprise import CounterpartyType
from domain.financial import TransactionDirection, TransactionStatus, TransactionType
from pydantic import Field

from schemas.base import SchemaModel


class FinancialTransactionCreateSchema(SchemaModel):
    """Canonical transaction persistence payload."""

    enterprise_id: UUID
    ingestion_source_id: UUID
    ingestion_run_id: UUID
    counterparty_id: UUID | None = None
    transaction_type: TransactionType
    transaction_date: date
    due_date: date | None = None
    settlement_date: date | None = None
    amount: Decimal = Field(gt=0)
    currency_code: str = Field(min_length=3, max_length=3, pattern=r'^[A-Z]{3}$')
    direction: TransactionDirection
    status: TransactionStatus
    reference_number: str | None = None
    description: str | None = None
    source_record_id: str = Field(min_length=1)
    source_payload_hash: str | None = None
    counterparty_external_key: str | None = None
    counterparty_name: str | None = None
    counterparty_type: CounterpartyType | None = None


class FinancialTransactionSchema(FinancialTransactionCreateSchema):
    """Financial transaction response schema."""

    id: UUID
    created_at: datetime
    updated_at: datetime


class FinancialTransactionUpdateSchema(SchemaModel):
    """Financial transaction update schema."""

    counterparty_id: UUID | None = None
    due_date: date | None = None
    settlement_date: date | None = None
    status: TransactionStatus | None = None
    reference_number: str | None = None
    description: str | None = None


class FinancialTransactionFilterParams(SchemaModel):
    """Financial transaction list filters."""

    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class CounterpartySchema(SchemaModel):
    """Counterparty response schema."""

    id: UUID
    enterprise_id: UUID
    external_key: str = Field(min_length=1)
    name: str = Field(min_length=1)
    counterparty_type: CounterpartyType
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CounterpartyCreateSchema(SchemaModel):
    """Counterparty creation schema."""

    external_key: str = Field(min_length=1)
    name: str = Field(min_length=1)
    counterparty_type: CounterpartyType
    is_active: bool = True


class CounterpartyUpdateSchema(SchemaModel):
    """Counterparty update schema."""

    name: str | None = Field(default=None, min_length=1)
    counterparty_type: CounterpartyType | None = None
    is_active: bool | None = None


class CounterpartyFilterParams(SchemaModel):
    """Counterparty list filters."""

    external_key: str | None = Field(default=None, min_length=1)
    name: str | None = Field(default=None, min_length=1)
    is_active: bool = True
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
