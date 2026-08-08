from decimal import Decimal
from typing import Protocol

from domain.exceptions import InvalidSimulationError


class ISimulationRules(Protocol):
    def validate_scenario(self, scenario_index: int, scenario_label: str) -> None: ...

    def validate_recommendation(
        self,
        *,
        priority_rank: int,
        parameter_name: str,
        expected_post_action_cashflow: Decimal,
        solvency_buffer: Decimal,
    ) -> None: ...


class DefaultSimulationRules:
    def validate_scenario(self, scenario_index: int, scenario_label: str) -> None:
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
        if priority_rank <= 0:
            raise InvalidSimulationError('Recommendation priority must be positive.')
        if not parameter_name.strip():
            raise InvalidSimulationError('Recommendation parameter must not be empty.')
        if expected_post_action_cashflow < solvency_buffer:
            raise InvalidSimulationError(
                'A recommendation must meet the configured solvency buffer.'
            )
