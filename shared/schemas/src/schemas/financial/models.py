from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from domain.enterprise import CounterpartyType
from domain.financial import (
    EntryMode,
    TransactionDirection,
    TransactionStatus,
    TransactionType,
)
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


class StaticFinancialSnapshotCreateSchema(SchemaModel):
    """Create a point-in-time static model feature snapshot."""

    snapshot_date: date
    entry_mode: EntryMode = EntryMode.MANUAL
    ingestion_source_id: UUID | None = None
    credit_score: Decimal | None = None
    failure_score: Decimal | None = None
    debt_to_revenue_ratio: Decimal | None = None
    current_assets: Decimal | None = Field(default=None, ge=0)
    current_liabilities: Decimal | None = Field(default=None, ge=0)
    fixed_assets: Decimal | None = Field(default=None, ge=0)
    long_term_liabilities: Decimal | None = Field(default=None, ge=0)
    capex: Decimal | None = Field(default=None, ge=0)
    cogs: Decimal | None = Field(default=None, ge=0)
    missed_payments_number: int | None = Field(default=None, ge=0)


class StaticFinancialSnapshotUpdateSchema(SchemaModel):
    """Update static snapshot values."""

    entry_mode: EntryMode | None = None
    ingestion_source_id: UUID | None = None
    credit_score: Decimal | None = None
    failure_score: Decimal | None = None
    debt_to_revenue_ratio: Decimal | None = None
    current_assets: Decimal | None = Field(default=None, ge=0)
    current_liabilities: Decimal | None = Field(default=None, ge=0)
    fixed_assets: Decimal | None = Field(default=None, ge=0)
    long_term_liabilities: Decimal | None = Field(default=None, ge=0)
    capex: Decimal | None = Field(default=None, ge=0)
    cogs: Decimal | None = Field(default=None, ge=0)
    missed_payments_number: int | None = Field(default=None, ge=0)


class StaticFinancialSnapshotSchema(StaticFinancialSnapshotCreateSchema):
    """Static financial snapshot response."""

    id: UUID
    enterprise_id: UUID
    created_at: datetime
    updated_at: datetime


class MonthlyCashflowAggregateCreateSchema(SchemaModel):
    """Persist one enterprise-month forecasting aggregate."""

    enterprise_id: UUID
    period_start: date
    period_end: date
    total_invoice_amount: Decimal
    total_inflows: Decimal
    total_outflows: Decimal
    monthly_repayment: Decimal
    total_payment_delay_days: Decimal
    invoice_count: int = Field(ge=0)
    payment_count: int = Field(ge=0)
    derived_from_run_id: UUID


class MonthlyCashflowAggregateUpdateSchema(SchemaModel):
    """Update derived enterprise-month forecasting values."""

    total_invoice_amount: Decimal
    total_inflows: Decimal
    total_outflows: Decimal
    monthly_repayment: Decimal
    total_payment_delay_days: Decimal
    invoice_count: int = Field(ge=0)
    payment_count: int = Field(ge=0)
    derived_from_run_id: UUID


class CounterpartyMonthlyReceivableCreateSchema(SchemaModel):
    """Persist one counterparty-month receivable aggregate."""

    enterprise_id: UUID
    counterparty_id: UUID
    period_start: date
    period_end: date
    invoice_total: Decimal
    amount_paid: Decimal
    outstanding_amount: Decimal
    average_payment_delay_days: Decimal | None = None
    late_invoice_count: int = Field(ge=0)


class CounterpartyMonthlyReceivableUpdateSchema(SchemaModel):
    """Update derived counterparty-month receivable values."""

    invoice_total: Decimal
    amount_paid: Decimal
    outstanding_amount: Decimal
    average_payment_delay_days: Decimal | None = None
    late_invoice_count: int = Field(ge=0)
