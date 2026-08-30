from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from domain.forecasting import ForecastRunType, ForecastStatus
from pydantic import Field, model_validator

from schemas.base import SchemaModel
from schemas.financial import StaticFinancialSnapshotSchema


class ForecastRequestSchema(SchemaModel):
    """Request a baseline forecast for one target month."""

    target_period_start: date
    target_period_end: date
    run_type: ForecastRunType = ForecastRunType.AD_HOC_BASELINE
    solvency_buffer: Decimal = Field(ge=0)

    @model_validator(mode='after')
    def validate_target_period(self) -> 'ForecastRequestSchema':
        """Ensure the target range is ordered."""
        if self.target_period_end < self.target_period_start:
            raise ValueError('target_period_end cannot precede target_period_start.')
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
    period_start: date
    period_end: date
    total_invoice_amount: Decimal
    total_inflows: Decimal
    total_outflows: Decimal
    monthly_repayment: Decimal
    total_payment_delay_days: Decimal
    invoice_count: int = Field(ge=0)
    payment_count: int = Field(ge=0)
    net_cashflow: Decimal


class ForecastObservationDriverSchema(SchemaModel):
    """One observed input driver used by the forecast model."""

    label: str
    value: Decimal
    detail: str


class ForecastFilterParams(SchemaModel):
    """Filters and pagination parameters for forecast history."""

    run_type: ForecastRunType | None = None
    status: ForecastStatus | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


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
    static_snapshot: StaticFinancialSnapshotSchema | None = None
    expected_inflows: Decimal = Decimal(0)
    expected_outflows: Decimal = Decimal(0)
    observation_drivers: list[ForecastObservationDriverSchema] = Field(
        default_factory=list
    )
    observations: list[str] = Field(default_factory=list)
