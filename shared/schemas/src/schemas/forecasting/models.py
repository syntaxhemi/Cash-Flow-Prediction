from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from domain.forecasting import ForecastRunType, ForecastStatus
from pydantic import Field, model_validator

from schemas.base import SchemaModel


class ForecastRequestSchema(SchemaModel):
    """Request a baseline forecast for one target month."""

    target_period_start: date
    target_period_end: date
    run_type: ForecastRunType = ForecastRunType.AD_HOC_BASELINE
    solvency_buffer: Decimal = Field(ge=0)

    @model_validator(mode='after')
    def validate_target_period(self) -> 'ForecastRequestSchema':
        """Ensure the target range describes exactly one calendar month."""
        if self.target_period_start.day != 1:
            raise ValueError('target_period_start must be the first day of a month.')
        if self.target_period_end < self.target_period_start:
            raise ValueError('target_period_end cannot precede target_period_start.')
        if self.target_period_end.month != self.target_period_start.month:
            raise ValueError('Forecast target must contain one calendar month.')
        return self


class ForecastRunCreateSchema(SchemaModel):
    """Complete persistence payload for a forecast run."""

    enterprise_id: UUID
    run_type: ForecastRunType
    target_period_start: date
    target_period_end: date
    sequence_window_months: int = Field(ge=1)
    static_snapshot_id: UUID
    model_version: str = Field(min_length=1, max_length=100)
    artifact_version: str = Field(min_length=1, max_length=100)
    predicted_net_cashflow: Decimal
    solvency_buffer: Decimal = Field(ge=0)
    buffer_gap: Decimal
    status: ForecastStatus
    requested_at: datetime
    completed_at: datetime | None = None


class ForecastRunPeriodCreateSchema(SchemaModel):
    """Persist one aggregate selected for a forecast sequence."""

    monthly_cashflow_aggregate_id: UUID
    sequence_index: int = Field(ge=0)


class ForecastRunPeriodSchema(ForecastRunPeriodCreateSchema):
    """Forecast sequence period response."""

    id: UUID
    forecast_run_id: UUID


class ForecastRunSchema(SchemaModel):
    """Baseline forecast response and audit metadata."""

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
    periods: list[ForecastRunPeriodSchema] = Field(default_factory=list)
