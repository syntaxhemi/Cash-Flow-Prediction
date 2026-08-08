from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from domain.enterprise import CounterpartyType
from domain.financial import (
    EntryMode,
    TransactionDirection,
    TransactionStatus,
    TransactionType,
)
from sqlalchemy import (
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database.base import Base
from database.utils import enum_type

if TYPE_CHECKING:
    from database.models.enterprise import EnterpriseModel
    from database.models.ingestion import IngestionRunModel, IngestionSourceModel

Money = Numeric(19, 4)


class CounterpartyModel(Base):
    __tablename__ = 'counterparties'
    __table_args__ = (
        UniqueConstraint('enterprise_id', 'external_key'),
        Index('ix_counterparties_enterprise_id', 'enterprise_id'),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    enterprise_id: Mapped[UUID] = mapped_column(
        ForeignKey('enterprises.id'), nullable=False
    )
    external_key: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    counterparty_type: Mapped[CounterpartyType] = mapped_column(
        enum_type(CounterpartyType, name='counterparty_type'), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    enterprise: Mapped['EnterpriseModel'] = relationship()
    transactions: Mapped[list['FinancialTransactionModel']] = relationship(
        back_populates='counterparty'
    )


class FinancialTransactionModel(Base):
    __tablename__ = 'financial_transactions'
    __table_args__ = (
        UniqueConstraint('ingestion_source_id', 'source_record_id'),
        Index(
            'ix_financial_transactions_enterprise_id_transaction_date',
            'enterprise_id',
            'transaction_date',
        ),
        Index(
            'ix_financial_transactions_enterprise_counterparty_date',
            'enterprise_id',
            'counterparty_id',
            'transaction_date',
        ),
        Index('ix_financial_transactions_ingestion_run_id', 'ingestion_run_id'),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    enterprise_id: Mapped[UUID] = mapped_column(
        ForeignKey('enterprises.id'), nullable=False
    )
    ingestion_source_id: Mapped[UUID] = mapped_column(
        ForeignKey('ingestion_sources.id'), nullable=False
    )
    ingestion_run_id: Mapped[UUID] = mapped_column(
        ForeignKey('ingestion_runs.id'), nullable=False
    )
    counterparty_id: Mapped[UUID | None] = mapped_column(
        ForeignKey('counterparties.id')
    )
    transaction_type: Mapped[TransactionType] = mapped_column(
        enum_type(TransactionType, name='transaction_type'), nullable=False
    )
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date)
    settlement_date: Mapped[date | None] = mapped_column(Date)
    amount: Mapped[Decimal] = mapped_column(Money, nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    direction: Mapped[TransactionDirection] = mapped_column(
        enum_type(TransactionDirection, name='transaction_direction'), nullable=False
    )
    status: Mapped[TransactionStatus] = mapped_column(
        enum_type(TransactionStatus, name='transaction_status'), nullable=False
    )
    reference_number: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(2000))
    source_record_id: Mapped[str] = mapped_column(String(255), nullable=False)
    source_payload_hash: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    enterprise: Mapped['EnterpriseModel'] = relationship()
    counterparty: Mapped[CounterpartyModel | None] = relationship(
        back_populates='transactions'
    )
    ingestion_source: Mapped['IngestionSourceModel'] = relationship()
    ingestion_run: Mapped['IngestionRunModel'] = relationship()


class MonthlyCashflowAggregateModel(Base):
    __tablename__ = 'monthly_cashflow_aggregates'
    __table_args__ = (
        UniqueConstraint('enterprise_id', 'period_start', 'period_end'),
        Index(
            'ix_monthly_cashflow_aggregates_enterprise_id_period_start',
            'enterprise_id',
            'period_start',
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    enterprise_id: Mapped[UUID] = mapped_column(
        ForeignKey('enterprises.id'), nullable=False
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    total_invoice_amount: Mapped[Decimal] = mapped_column(Money, nullable=False)
    total_inflows: Mapped[Decimal] = mapped_column(Money, nullable=False)
    total_outflows: Mapped[Decimal] = mapped_column(Money, nullable=False)
    monthly_repayment: Mapped[Decimal] = mapped_column(Money, nullable=False)
    average_payment_delay_days: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    invoice_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    payment_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    derived_from_run_id: Mapped[UUID] = mapped_column(
        ForeignKey('ingestion_runs.id'), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    enterprise: Mapped['EnterpriseModel'] = relationship()
    derived_from_run: Mapped['IngestionRunModel'] = relationship()


class CounterpartyMonthlyReceivableModel(Base):
    __tablename__ = 'counterparty_monthly_receivables'
    __table_args__ = (
        UniqueConstraint(
            'enterprise_id', 'counterparty_id', 'period_start', 'period_end'
        ),
        Index(
            'ix_counterparty_monthly_receivables_enterprise_id_period_start',
            'enterprise_id',
            'period_start',
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    enterprise_id: Mapped[UUID] = mapped_column(
        ForeignKey('enterprises.id'), nullable=False
    )
    counterparty_id: Mapped[UUID] = mapped_column(
        ForeignKey('counterparties.id'), nullable=False
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    invoice_total: Mapped[Decimal] = mapped_column(Money, nullable=False)
    amount_paid: Mapped[Decimal] = mapped_column(Money, nullable=False)
    outstanding_amount: Mapped[Decimal] = mapped_column(Money, nullable=False)
    average_payment_delay_days: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    late_invoice_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    enterprise: Mapped['EnterpriseModel'] = relationship()
    counterparty: Mapped[CounterpartyModel] = relationship()


class StaticFinancialSnapshotModel(Base):
    __tablename__ = 'static_financial_snapshots'
    __table_args__ = (
        UniqueConstraint('enterprise_id', 'snapshot_date'),
        Index(
            'ix_static_financial_snapshots_enterprise_id_snapshot_date',
            'enterprise_id',
            'snapshot_date',
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    enterprise_id: Mapped[UUID] = mapped_column(
        ForeignKey('enterprises.id'), nullable=False
    )
    ingestion_source_id: Mapped[UUID | None] = mapped_column(
        ForeignKey('ingestion_sources.id')
    )
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    entry_mode: Mapped[EntryMode] = mapped_column(
        enum_type(EntryMode, name='entry_mode'), nullable=False
    )
    credit_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    failure_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    debt_to_revenue_ratio: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    current_assets: Mapped[Decimal | None] = mapped_column(Money)
    current_liabilities: Mapped[Decimal | None] = mapped_column(Money)
    fixed_assets: Mapped[Decimal | None] = mapped_column(Money)
    long_term_liabilities: Mapped[Decimal | None] = mapped_column(Money)
    capex: Mapped[Decimal | None] = mapped_column(Money)
    cogs: Mapped[Decimal | None] = mapped_column(Money)
    missed_payments_number: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    enterprise: Mapped['EnterpriseModel'] = relationship()
    ingestion_source: Mapped['IngestionSourceModel | None'] = relationship()
