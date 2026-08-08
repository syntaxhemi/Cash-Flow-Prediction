from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from domain.enterprise.enums import CounterpartyType
from domain.financial.enums import (
    EntryMode,
    TransactionDirection,
    TransactionStatus,
    TransactionType,
)


@dataclass(frozen=True, slots=True)
class Counterparty:
    id: UUID
    enterprise_id: UUID
    external_key: str
    name: str
    counterparty_type: CounterpartyType
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class FinancialTransaction:
    id: UUID
    enterprise_id: UUID
    ingestion_source_id: UUID
    ingestion_run_id: UUID
    counterparty_id: UUID | None
    transaction_type: TransactionType
    transaction_date: date
    due_date: date | None
    settlement_date: date | None
    amount: Decimal
    currency_code: str
    direction: TransactionDirection
    status: TransactionStatus
    reference_number: str | None
    description: str | None
    source_record_id: str
    source_payload_hash: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class MonthlyCashflowAggregate:
    id: UUID
    enterprise_id: UUID
    period_start: date
    period_end: date
    total_invoice_amount: Decimal
    total_inflows: Decimal
    total_outflows: Decimal
    monthly_repayment: Decimal
    average_payment_delay_days: Decimal | None
    invoice_count: int
    payment_count: int
    derived_from_run_id: UUID
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class CounterpartyMonthlyReceivable:
    id: UUID
    enterprise_id: UUID
    counterparty_id: UUID
    period_start: date
    period_end: date
    invoice_total: Decimal
    amount_paid: Decimal
    outstanding_amount: Decimal
    average_payment_delay_days: Decimal | None
    late_invoice_count: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class StaticFinancialSnapshot:
    id: UUID
    enterprise_id: UUID
    ingestion_source_id: UUID | None
    snapshot_date: date
    entry_mode: EntryMode
    credit_score: Decimal | None
    failure_score: Decimal | None
    debt_to_revenue_ratio: Decimal | None
    current_assets: Decimal | None
    current_liabilities: Decimal | None
    fixed_assets: Decimal | None
    long_term_liabilities: Decimal | None
    capex: Decimal | None
    cogs: Decimal | None
    missed_payments_number: int | None
    created_at: datetime
    updated_at: datetime
