from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from domain.simulation.enums import (
    RecommendationActionType,
    SimulationStatus,
    SimulationType,
)


@dataclass(frozen=True, slots=True)
class SimulationRun:
    id: UUID
    enterprise_id: UUID
    forecast_run_id: UUID
    simulation_type: SimulationType
    status: SimulationStatus
    summary_result: dict[str, Any]
    requested_at: datetime
    completed_at: datetime | None
    created_at: datetime


@dataclass(frozen=True, slots=True)
class SimulationScenario:
    id: UUID
    simulation_run_id: UUID
    scenario_index: int
    scenario_label: str
    input_patch: dict[str, Any]
    predicted_net_cashflow: Decimal
    delta_from_baseline: Decimal
    meets_buffer: bool
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ReceivablesRanking:
    id: UUID
    simulation_run_id: UUID
    counterparty_id: UUID
    rank_position: int
    baseline_outstanding_amount: Decimal
    simulated_cashflow_delta: Decimal
    created_at: datetime


@dataclass(frozen=True, slots=True)
class MitigationRecommendation:
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
