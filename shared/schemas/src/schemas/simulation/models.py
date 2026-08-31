from datetime import datetime
from decimal import Decimal
from math import isfinite
from typing import Any
from uuid import UUID

from domain.scoring import HealthStatus
from domain.simulation import (
    HealthDeltaProfile,
    LiquidityMitigationProfile,
    RecommendationActionType,
    SimulationStatus,
    SimulationType,
)
from pydantic import Field, field_validator, model_validator

from schemas.base import SchemaModel


class HealthDeltaRequestSchema(SchemaModel):
    """Request a server-generated health delta sensitivity profile."""

    profile: HealthDeltaProfile = HealthDeltaProfile.STANDARD
    features: dict[str, Decimal] = Field(default_factory=dict)

    @field_validator('features')
    @classmethod
    def validate_features(cls, value: dict[str, Decimal]) -> dict[str, Decimal]:
        """Ensure custom feature overrides are finite and non-negative.

        Args:
            value: Optional user-selected static feature targets.

        Returns:
            The validated feature targets.

        Raises:
            ValueError: If a target is negative or non-finite.
        """
        for name, target in value.items():
            numeric_target = float(target)
            if numeric_target < 0 or not isfinite(numeric_target):
                raise ValueError(
                    f'Feature target "{name}" must be finite and non-negative.'
                )
        return value


class SimulationRunCreateSchema(SchemaModel):
    """Persistence payload for a simulation run."""

    enterprise_id: UUID
    forecast_run_id: UUID
    simulation_type: SimulationType
    status: SimulationStatus
    summary_result: dict[str, Any] = Field(default_factory=dict)
    requested_at: datetime
    completed_at: datetime | None = None


class SimulationRunUpdateSchema(SchemaModel):
    """Mutable persistence fields for a simulation run."""

    status: SimulationStatus | None = None
    summary_result: dict[str, Any] | None = None
    completed_at: datetime | None = None


class SimulationScenarioCreateSchema(SchemaModel):
    """Persistence payload for one simulation scenario."""

    scenario_index: int = Field(ge=0)
    scenario_label: str = Field(min_length=1, max_length=255)
    input_patch_json: dict[str, Any]
    predicted_net_cashflow: Decimal
    delta_from_baseline: Decimal
    meets_buffer: bool
    health_score: Decimal | None = Field(default=None, ge=0, le=100)
    health_score_delta: Decimal | None = Field(default=None, ge=-100, le=100)
    health_status: HealthStatus | None = None


class SimulationScenarioUpdateSchema(SchemaModel):
    """Mutable persistence fields for a simulation scenario."""

    scenario_label: str | None = Field(default=None, min_length=1, max_length=255)
    input_patch_json: dict[str, Any] | None = None
    predicted_net_cashflow: Decimal | None = None
    delta_from_baseline: Decimal | None = None
    meets_buffer: bool | None = None


class ReceivablesRankingCreateSchema(SchemaModel):
    """Persistence payload for a receivables ranking."""

    counterparty_id: UUID
    rank_position: int = Field(ge=1)
    baseline_outstanding_amount: Decimal
    simulated_cashflow_delta: Decimal


class ReceivablesRankingUpdateSchema(SchemaModel):
    """Mutable persistence fields for a receivables ranking."""

    rank_position: int | None = Field(default=None, ge=1)
    baseline_outstanding_amount: Decimal | None = None
    simulated_cashflow_delta: Decimal | None = None


class TrappedLiquidityRequestSchema(SchemaModel):
    """Request trapped-liquidity analysis for selected counterparties."""

    counterparty_ids: list[UUID] | None = Field(default=None, max_length=50)
    max_counterparties: int = Field(default=10, ge=1, le=50)


class ReceivablesRankingSchema(SchemaModel):
    """Persisted trapped-liquidity ranking response."""

    id: UUID
    simulation_run_id: UUID
    counterparty_id: UUID
    rank_position: int
    baseline_outstanding_amount: Decimal
    simulated_cashflow_delta: Decimal
    created_at: datetime


class MitigationRecommendationCreateSchema(SchemaModel):
    """Persistence payload for a mitigation recommendation."""

    priority_rank: int = Field(ge=1)
    action_type: RecommendationActionType
    parameter_name: str = Field(min_length=1, max_length=255)
    original_value: Decimal
    recommended_value: Decimal
    expected_cashflow_delta: Decimal
    expected_post_action_cashflow: Decimal
    meets_buffer: bool


class MitigationRecommendationUpdateSchema(SchemaModel):
    """Mutable persistence fields for a mitigation recommendation."""

    priority_rank: int | None = Field(default=None, ge=1)
    action_type: RecommendationActionType | None = None
    parameter_name: str | None = Field(default=None, min_length=1, max_length=255)
    original_value: Decimal | None = None
    recommended_value: Decimal | None = None
    expected_cashflow_delta: Decimal | None = None
    expected_post_action_cashflow: Decimal | None = None
    meets_buffer: bool | None = None


class LiquidityMitigationRequestSchema(SchemaModel):
    """Request bounded liquidity mitigation recommendations."""

    profile: LiquidityMitigationProfile = LiquidityMitigationProfile.STANDARD
    max_recommendations: int = Field(default=3, ge=1, le=3)


class SimulationFilterParams(SchemaModel):
    """Filters for enterprise-scoped simulation result listings."""

    simulation_type: SimulationType | None = None
    status: SimulationStatus | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

    @model_validator(mode='after')
    def validate_created_window(self) -> 'SimulationFilterParams':
        """Ensure the created-time window is ordered.

        Returns:
            The validated filter parameters.

        Raises:
            ValueError: If ``created_from`` is after ``created_to``.
        """
        if (
            self.created_from is not None
            and self.created_to is not None
            and self.created_from > self.created_to
        ):
            raise ValueError('created_from must not be after created_to.')
        return self


class MitigationRecommendationSchema(SchemaModel):
    """Persisted liquidity mitigation recommendation response."""

    id: UUID
    simulation_run_id: UUID
    priority_rank: int
    action_type: RecommendationActionType
    parameter_name: str
    original_value: Decimal
    recommended_value: Decimal
    expected_cashflow_delta: Decimal
    expected_post_action_cashflow: Decimal
    meets_buffer: bool
    created_at: datetime


class SimulationScenarioSchema(SimulationScenarioCreateSchema):
    """Persisted simulation scenario response."""

    id: UUID
    simulation_run_id: UUID
    created_at: datetime


class SimulationRunSchema(SchemaModel):
    """Simulation run response with persisted scenarios."""

    id: UUID
    enterprise_id: UUID
    forecast_run_id: UUID
    simulation_type: SimulationType
    status: SimulationStatus
    summary_result: dict[str, Any]
    requested_at: datetime
    completed_at: datetime | None
    created_at: datetime
    scenarios: list[SimulationScenarioSchema] = Field(default_factory=list)
    receivables_rankings: list[ReceivablesRankingSchema] = Field(default_factory=list)
    mitigation_recommendations: list[MitigationRecommendationSchema] = Field(
        default_factory=list
    )
