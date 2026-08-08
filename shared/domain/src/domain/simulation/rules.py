from decimal import Decimal
from typing import Protocol

from domain.exceptions import InvalidSimulationError


class ISimulationRules(Protocol):
    def validate_scenario(self, scenario_index: int, scenario_label: str) -> None:
        """Validate scenario identity fields."""
        ...

    def validate_recommendation(
        self,
        *,
        priority_rank: int,
        parameter_name: str,
        expected_post_action_cashflow: Decimal,
        solvency_buffer: Decimal,
    ) -> None:
        """Validate recommendation priority and buffer outcome."""
        ...


class DefaultSimulationRules:
    def validate_scenario(self, scenario_index: int, scenario_label: str) -> None:
        """Validate scenario ordering and label.

        Args:
            scenario_index: Zero-based scenario position.
            scenario_label: Human-readable scenario label.

        Raises:
            InvalidSimulationError: If the index or label is invalid.
        """
        if scenario_index < 0:
            raise InvalidSimulationError('Scenario index must be non-negative.')
        if not scenario_label.strip():
            raise InvalidSimulationError('Scenario label must not be empty.')

    def validate_recommendation(
        self,
        *,
        priority_rank: int,
        parameter_name: str,
        expected_post_action_cashflow: Decimal,
        solvency_buffer: Decimal,
    ) -> None:
        """Validate a recommendation against the solvency buffer.

        Args:
            priority_rank: Positive recommendation priority.
            parameter_name: Financial parameter being changed.
            expected_post_action_cashflow: Projected cash flow after action.
            solvency_buffer: Required minimum cash flow buffer.

        Raises:
            InvalidSimulationError: If the recommendation is invalid.
        """
        if priority_rank <= 0:
            raise InvalidSimulationError('Recommendation priority must be positive.')
        if not parameter_name.strip():
            raise InvalidSimulationError('Recommendation parameter must not be empty.')
        if expected_post_action_cashflow < solvency_buffer:
            raise InvalidSimulationError(
                'A recommendation must meet the configured solvency buffer.'
            )
