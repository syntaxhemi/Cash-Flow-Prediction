from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from domain.forecasting.enums import ForecastRunType, ForecastStatus


@dataclass(frozen=True, slots=True)
class ForecastRun:
    id: UUID
    enterprise_id: UUID
    run_type: ForecastRunType
    target_period_start: date
    target_period_end: date
    sequence_window_months: int
    static_snapshot_id: UUID
    model_version: str
    artifact_version: str
    predicted_net_cashflow: Decimal
    solvency_buffer: Decimal
    buffer_gap: Decimal
    status: ForecastStatus
    requested_at: datetime
    completed_at: datetime | None
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ForecastRunPeriod:
    id: UUID
    forecast_run_id: UUID
    monthly_cashflow_aggregate_id: UUID
    sequence_index: int
