from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

from database import IUnitOfWork
from domain.exceptions import InvalidForecastRunError, InvalidSimulationError
from domain.forecasting import ForecastStatus
from domain.scoring import (
    HEALTH_SCORE_FEATURES,
    calculate_health_score,
    classify_health_score,
)
from domain.simulation import HealthDeltaProfile, SimulationStatus, SimulationType
from ml import ModelArtifactLoader
from schemas.simulation import (
    HealthDeltaRequestSchema,
    SimulationRunCreateSchema,
    SimulationRunSchema,
    SimulationRunUpdateSchema,
    SimulationScenarioCreateSchema,
    SimulationScenarioSchema,
)

from api.services.forecasting.counterfactual import (
    CounterfactualContext,
    CounterfactualEvaluator,
    build_counterfactual_context,
)


class HealthDeltaSimulationService:
    """Orchestrate and persist health delta simulations."""

    def __init__(self, uow: IUnitOfWork, artifact_directory: str) -> None:
        """Initialize the health delta simulation service.

        Args:
            uow: Unit of work used to load baseline inputs and persist simulation data.
            artifact_directory: Directory containing the selected model artifacts.
        """
        self._uow = uow
        self._artifact_loader = ModelArtifactLoader(Path(artifact_directory))
        self._evaluator = CounterfactualEvaluator()

    async def create(
        self,
        enterprise_id: UUID,
        forecast_run_id: UUID,
        payload: HealthDeltaRequestSchema,
    ) -> SimulationRunSchema:
        """Create and execute one health delta simulation.

        Args:
            enterprise_id: Owning enterprise identifier.
            forecast_run_id: Completed baseline forecast identifier.
            payload: Bounded static-feature scenarios to evaluate.

        Returns:
            The completed simulation run and its persisted scenarios.

        Raises:
            InvalidForecastRunError: If the baseline forecast is missing, belongs to a
                different enterprise, or is not completed.
            InvalidSimulationError: If baseline inputs or a scenario are invalid.
        """
        enterprise = await self._uow.enterprises.get_active_by_id_or_raise(
            enterprise_id
        )

        forecast = await self._uow.forecasts.get_by_id_with_inputs(
            enterprise_id, forecast_run_id
        )

        if forecast is None or forecast.enterprise_id != enterprise_id:
            raise InvalidForecastRunError(
                f'Forecast run "{forecast_run_id}" does not belong to the enterprise.'
            )

        if forecast.status is not ForecastStatus.COMPLETED:
            raise InvalidForecastRunError(
                'Health delta simulation requires a completed baseline forecast.'
            )

        artifacts = self._artifact_loader.load()
        context = build_counterfactual_context(
            forecast, artifacts.metadata, enterprise.base_currency
        )
        baseline_health_score = calculate_health_score(context.static_values)
        requested_at = datetime.now(UTC)
        run = await self._uow.simulation_runs.create(
            SimulationRunCreateSchema(
                enterprise_id=enterprise_id,
                forecast_run_id=forecast_run_id,
                simulation_type=SimulationType.HEALTH_DELTA,
                status=SimulationStatus.PENDING,
                requested_at=requested_at,
            )
        )
        await self._uow.commit()

        try:
            await self._uow.simulation_runs.update(
                run.id,
                payload=SimulationRunUpdateSchema(status=SimulationStatus.RUNNING),
            )
            await self._uow.commit()
            scenario_payloads = []

            for index, (label, input_patch) in enumerate(
                self._build_scenario_specs(context, payload)
            ):
                evaluation = self._evaluator.evaluate(context, input_patch, artifacts)
                scenario_values: dict[str, Decimal | float] = dict(
                    context.static_values
                )
                scenario_values.update(input_patch)
                scenario_health_score = calculate_health_score(scenario_values)
                scenario_payloads.append(
                    SimulationScenarioCreateSchema(
                        scenario_index=index,
                        scenario_label=label,
                        input_patch_json={
                            name: str(value) for name, value in input_patch.items()
                        },
                        predicted_net_cashflow=evaluation.predicted_net_cashflow,
                        delta_from_baseline=evaluation.delta_from_baseline,
                        meets_buffer=evaluation.meets_buffer,
                        health_score=scenario_health_score,
                        health_score_delta=scenario_health_score
                        - baseline_health_score,
                        health_status=classify_health_score(scenario_health_score),
                    )
                )

            await self._uow.simulation_scenarios.create_many(run.id, scenario_payloads)
            summary = self._build_summary(
                context, payload.profile, baseline_health_score, scenario_payloads
            )
            run = await self._uow.simulation_runs.update(
                run.id,
                payload=SimulationRunUpdateSchema(
                    status=SimulationStatus.COMPLETED,
                    summary_result=summary,
                    completed_at=datetime.now(UTC),
                ),
            )
            await self._uow.commit()

        except Exception as error:
            await self._uow.rollback()
            await self._uow.simulation_runs.update(
                run.id,
                payload=SimulationRunUpdateSchema(
                    status=SimulationStatus.FAILED,
                    summary_result={'error': str(error)},
                    completed_at=datetime.now(UTC),
                ),
            )
            await self._uow.commit()
            raise

        scenarios = await self._uow.simulation_scenarios.list_for_run(run.id)
        return SimulationRunSchema(
            id=run.id,
            enterprise_id=run.enterprise_id,
            forecast_run_id=run.forecast_run_id,
            simulation_type=run.simulation_type,
            status=run.status,
            summary_result=run.summary_result,
            requested_at=run.requested_at,
            completed_at=run.completed_at,
            created_at=run.created_at,
            scenarios=[
                SimulationScenarioSchema.model_validate(row) for row in scenarios
            ],
        )

    @staticmethod
    def _build_summary(
        context: CounterfactualContext,
        profile: HealthDeltaProfile,
        baseline_health_score: Decimal,
        scenarios: list[SimulationScenarioCreateSchema],
    ) -> dict[str, Any]:
        """Build a compact persisted health delta summary.

        Args:
            context: Baseline simulation context.
            profile: Server-defined profile used to generate scenarios.
            scenarios: Evaluated scenario persistence payloads.

        Returns:
            JSON-compatible summary values.
        """
        best = max(scenarios, key=lambda scenario: scenario.delta_from_baseline)
        best_health = max(
            scenarios,
            key=lambda scenario: (
                scenario.health_score_delta
                if scenario.health_score_delta is not None
                else Decimal('-Infinity')
            ),
        )
        return {
            'profile': profile.value,
            'baseline_prediction': str(context.baseline_prediction),
            'solvency_buffer': str(context.solvency_buffer),
            'baseline_health_score': str(baseline_health_score),
            'best_scenario_index': best.scenario_index,
            'best_delta_from_baseline': str(best.delta_from_baseline),
            'best_predicted_net_cashflow': str(best.predicted_net_cashflow),
            'best_meets_buffer': best.meets_buffer,
            'best_health_scenario_index': best_health.scenario_index,
            'best_health_score': str(best_health.health_score),
            'best_health_delta': str(best_health.health_score_delta),
            'best_health_status': best_health.health_status.value
            if best_health.health_status is not None
            else None,
        }

    @staticmethod
    def _build_scenario_specs(
        context: CounterfactualContext,
        payload: HealthDeltaRequestSchema,
    ) -> list[tuple[str, dict[str, Decimal]]]:
        """Generate bounded scenarios from a profile and optional feature targets.

        Args:
            context: Baseline static values used for relative scenarios.
            payload: Profile and optional user-selected feature targets.

        Returns:
            Scenario labels and static-feature patches.

        Raises:
            InvalidSimulationError: If the profile or selected features is invalid.
        """
        eligible_features = HEALTH_SCORE_FEATURES
        selected_features = list(payload.features) or list(eligible_features)
        unknown_features = set(selected_features) - set(eligible_features)

        if unknown_features:
            names = ', '.join(sorted(unknown_features))
            raise InvalidSimulationError(f'Unsupported health features: {names}.')

        if payload.profile is HealthDeltaProfile.CUSTOM and not payload.features:
            raise InvalidSimulationError(
                'The custom health delta profile requires selected feature targets.'
            )

        if payload.features:
            for feature, target in payload.features.items():
                baseline = Decimal(str(context.static_values[feature]))
                upper_bound = max(Decimal(1), baseline * Decimal(2))

                if target > upper_bound:
                    raise InvalidSimulationError(
                        f'Target for "{feature}" exceeds the configured simulation '
                        f'bound of {upper_bound}.'
                    )

            return [
                (f'{feature} target', {feature: target})
                for feature, target in payload.features.items()
            ]

        profile_delta = {
            HealthDeltaProfile.CONSERVATIVE: Decimal('0.05'),
            HealthDeltaProfile.STANDARD: Decimal('0.10'),
            HealthDeltaProfile.STRESS: Decimal('0.20'),
        }.get(payload.profile)
        if profile_delta is None:
            raise InvalidSimulationError(
                'A non-custom health delta profile is required when no targets are '
                'provided.'
            )

        scenarios: list[tuple[str, dict[str, Decimal]]] = []
        for feature in selected_features:
            baseline = Decimal(str(context.static_values[feature]))
            if baseline == 0:
                lower = Decimal(0)
                upper = Decimal(1)
            else:
                lower = max(Decimal(0), baseline * (Decimal(1) - profile_delta))
                upper = min(
                    baseline * Decimal(2),
                    baseline * (Decimal(1) + profile_delta),
                )
            scenarios.extend(
                [
                    (f'{feature} lower sensitivity', {feature: lower}),
                    (f'{feature} upper sensitivity', {feature: upper}),
                ]
            )
        return scenarios
