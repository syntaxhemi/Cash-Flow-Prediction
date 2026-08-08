from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from domain.forecasting import ForecastRunType, ForecastStatus
from sqlalchemy import Date, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database.base import Base
from database.utils import enum_type

if TYPE_CHECKING:
    from database.models.enterprise import EnterpriseModel
    from database.models.financial import (
        MonthlyCashflowAggregateModel,
        StaticFinancialSnapshotModel,
    )
    from database.models.simulation import SimulationRunModel


class ForecastRunModel(Base):
    __tablename__ = 'forecast_runs'
    __table_args__ = (
        Index(
            'ix_forecast_runs_enterprise_id_created_at', 'enterprise_id', 'created_at'
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    enterprise_id: Mapped[UUID] = mapped_column(
        ForeignKey('enterprises.id'), nullable=False
    )
    run_type: Mapped[ForecastRunType] = mapped_column(
        enum_type(ForecastRunType, name='forecast_run_type'), nullable=False
    )
    target_period_start: Mapped[date] = mapped_column(Date, nullable=False)
    target_period_end: Mapped[date] = mapped_column(Date, nullable=False)
    sequence_window_months: Mapped[int] = mapped_column(Integer, nullable=False)
    static_snapshot_id: Mapped[UUID] = mapped_column(
        ForeignKey('static_financial_snapshots.id'), nullable=False
    )
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    artifact_version: Mapped[str] = mapped_column(String(100), nullable=False)
    predicted_net_cashflow: Mapped[Decimal] = mapped_column(
        Numeric(19, 4), nullable=False
    )
    solvency_buffer: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    buffer_gap: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    status: Mapped[ForecastStatus] = mapped_column(
        enum_type(ForecastStatus, name='forecast_status'), nullable=False
    )
    requested_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    enterprise: Mapped['EnterpriseModel'] = relationship()
    static_snapshot: Mapped['StaticFinancialSnapshotModel'] = relationship()
    periods: Mapped[list['ForecastRunPeriodModel']] = relationship(
        back_populates='forecast_run'
    )
    simulation_runs: Mapped[list['SimulationRunModel']] = relationship(
        back_populates='forecast_run'
    )


class ForecastRunPeriodModel(Base):
    __tablename__ = 'forecast_run_periods'
    __table_args__ = (
        Index('ix_forecast_run_periods_forecast_run_id', 'forecast_run_id'),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    forecast_run_id: Mapped[UUID] = mapped_column(
        ForeignKey('forecast_runs.id'), nullable=False
    )
    monthly_cashflow_aggregate_id: Mapped[UUID] = mapped_column(
        ForeignKey('monthly_cashflow_aggregates.id'), nullable=False
    )
    sequence_index: Mapped[int] = mapped_column(Integer, nullable=False)

    forecast_run: Mapped[ForecastRunModel] = relationship(back_populates='periods')
    monthly_cashflow_aggregate: Mapped['MonthlyCashflowAggregateModel'] = relationship()
