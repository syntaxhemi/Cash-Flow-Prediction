from datetime import datetime
from decimal import Decimal
from math import isfinite
from typing import Any
from uuid import UUID

from domain.simulation import (
    HealthDeltaProfile,
    RecommendationActionType,
    SimulationStatus,
    SimulationType,
)
from pydantic import Field, field_validator

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
