from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from database import IUnitOfWork
from domain.exceptions import InvalidForecastRunError, InvalidSimulationError
from domain.forecasting import ForecastStatus
from domain.simulation import (
    LiquidityMitigationProfile,
    RecommendationActionType,
    SimulationStatus,
    SimulationType,
)
from domain.simulation.rules import DefaultSimulationRules
from ml import ModelArtifactLoader
from schemas.simulation import (
    LiquidityMitigationRequestSchema,
    MitigationRecommendationCreateSchema,
    MitigationRecommendationSchema,
    SimulationRunCreateSchema,
    SimulationRunSchema,
    SimulationRunUpdateSchema,
)

from api.services.forecasting.counterfactual import (
    CounterfactualContext,
    CounterfactualEvaluator,
    build_counterfactual_context,
)


@dataclass(frozen=True, slots=True)
class _MitigationCandidate:
    """One bounded action candidate before model evaluation."""

    action_type: RecommendationActionType
    parameter_name: str
    original_value: Decimal
    recommended_value: Decimal
    static_patch: dict[str, Decimal]
    temporal_patch: dict[int, dict[str, Decimal]]


class LiquidityMitigationService:
    """Orchestrate bounded liquidity mitigation recommendations."""

    def __init__(self, uow: IUnitOfWork, artifact_directory: str) -> None:
        """Initialize the liquidity mitigation service.

        Args:
            uow: Unit of work used to load inputs and persist recommendations.
            artifact_directory: Directory containing the selected model artifacts.
        """
        self._uow = uow
        self._artifact_loader = ModelArtifactLoader(Path(artifact_directory))
        self._evaluator = CounterfactualEvaluator()
        self._rules = DefaultSimulationRules()

    async def create(
        self,
        enterprise_id: UUID,
        forecast_run_id: UUID,
        payload: LiquidityMitigationRequestSchema,
    ) -> SimulationRunSchema:
        """Create and execute one liquidity mitigation simulation.

        Args:
            enterprise_id: Owning enterprise identifier.
            forecast_run_id: Completed baseline forecast identifier.
            payload: Bounded mitigation profile and result limit.

        Returns:
            The completed simulation run and persisted recommendations.

        Raises:
            InvalidForecastRunError: If the baseline forecast is missing, belongs to
                another enterprise, or is not completed.
            InvalidSimulationError: If the baseline does not breach its buffer or
                mitigation inputs are invalid.
        """
        await self._uow.enterprises.get_active_by_id_or_raise(enterprise_id)

        forecast = await self._uow.forecasts.get_by_id_with_inputs(forecast_run_id)
        if forecast is None or forecast.enterprise_id != enterprise_id:
            raise InvalidForecastRunError(
                f'Forecast run "{forecast_run_id}" does not belong to the enterprise.'
            )
        if forecast.status is not ForecastStatus.COMPLETED:
            raise InvalidForecastRunError(
                'Liquidity mitigation requires a completed baseline forecast.'
            )
        if forecast.predicted_net_cashflow >= forecast.solvency_buffer:
            raise InvalidSimulationError(
                'Liquidity mitigation requires a baseline forecast below its buffer.'
            )

        artifacts = self._artifact_loader.load()
        context = build_counterfactual_context(forecast, artifacts.metadata)
        candidates = self._build_candidates(context, payload.profile)
        if not candidates:
            raise InvalidSimulationError(
                'No bounded mitigation candidates can be generated from the baseline.'
            )

        run = await self._uow.simulation_runs.create(
            SimulationRunCreateSchema(
                enterprise_id=enterprise_id,
                forecast_run_id=forecast_run_id,
                simulation_type=SimulationType.LIQUIDITY_MITIGATION,
                status=SimulationStatus.PENDING,
                requested_at=datetime.now(UTC),
            )
        )
        await self._uow.commit()

        try:
            await self._uow.simulation_runs.update(
                run.id,
                payload=SimulationRunUpdateSchema(status=SimulationStatus.RUNNING),
            )
            await self._uow.commit()

            recommendations = []
            evaluated_count = 0
            for candidate in candidates:
                evaluation = self._evaluator.evaluate(
                    context,
                    candidate.static_patch,
                    artifacts,
                    temporal_patch=candidate.temporal_patch,
                )
                evaluated_count += 1
                if not evaluation.meets_buffer:
                    continue
                recommendations.append(
                    (
                        candidate,
                        context.baseline_prediction + evaluation.delta_from_baseline,
                        evaluation.delta_from_baseline,
                    )
                )

            recommendations.sort(key=lambda item: item[2], reverse=True)
            recommendation_payloads = []
            for rank, (candidate, post_action, delta) in enumerate(
                recommendations[: payload.max_recommendations], start=1
            ):
                self._rules.validate_recommendation(
                    priority_rank=rank,
                    parameter_name=candidate.parameter_name,
                    expected_post_action_cashflow=post_action,
                    solvency_buffer=context.solvency_buffer,
                )
                recommendation_payloads.append(
                    MitigationRecommendationCreateSchema(
                        priority_rank=rank,
                        action_type=candidate.action_type,
                        parameter_name=candidate.parameter_name,
                        original_value=candidate.original_value,
                        recommended_value=candidate.recommended_value,
                        expected_cashflow_delta=delta,
                        expected_post_action_cashflow=post_action,
                        meets_buffer=True,
                    )
                )
            await self._uow.mitigation_recommendations.create_many(
                run.id, recommendation_payloads
            )
            summary = {
                'profile': payload.profile.value,
                'baseline_prediction': str(context.baseline_prediction),
                'solvency_buffer': str(context.solvency_buffer),
                'evaluated_candidates': evaluated_count,
                'recommendation_count': len(recommendation_payloads),
            }
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

        rows = await self._uow.mitigation_recommendations.list_for_run(run.id)
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
            mitigation_recommendations=[
                MitigationRecommendationSchema.model_validate(row) for row in rows
            ],
        )

    @staticmethod
    def _build_candidates(
        context: CounterfactualContext, profile: LiquidityMitigationProfile
    ) -> list[_MitigationCandidate]:
        """Build server-bounded candidates for the selected mitigation profile.

        Args:
            context: Baseline feature values.
            profile: Bounded intervention profile.

        Returns:
            Candidate actions for model evaluation.
        """
        factors = {
            LiquidityMitigationProfile.CONSERVATIVE: (Decimal('0.9'),),
            LiquidityMitigationProfile.STANDARD: (
                Decimal('0.9'),
                Decimal('0.75'),
                Decimal('0.5'),
            ),
            LiquidityMitigationProfile.STRESS: (
                Decimal('0.75'),
                Decimal('0.5'),
                Decimal('0.25'),
            ),
        }[profile]
        latest_index = len(context.temporal_rows) - 1
        candidates: list[_MitigationCandidate] = []
        capex = Decimal(str(context.static_values['capex']))
        if capex > 0:
            candidates.append(
                _MitigationCandidate(
                    RecommendationActionType.DELAY_CAPEX,
                    'capex',
                    capex,
                    Decimal(0),
                    {'capex': Decimal(0)},
                    {},
                )
            )

        for factor in factors:
            outflows = Decimal(
                str(context.temporal_rows[latest_index]['total_outflows'])
            )

            if outflows > 0:
                candidates.append(
                    _MitigationCandidate(
                        RecommendationActionType.REDUCE_OUTFLOWS,
                        'total_outflows',
                        outflows,
                        outflows * factor,
                        {},
                        {latest_index: {'total_outflows': outflows * factor}},
                    )
                )

            repayment = Decimal(
                str(context.temporal_rows[latest_index]['monthly_repayment'])
            )

            if repayment > 0:
                candidates.append(
                    _MitigationCandidate(
                        RecommendationActionType.ADJUST_REPAYMENT,
                        'monthly_repayment',
                        repayment,
                        repayment * factor,
                        {},
                        {latest_index: {'monthly_repayment': repayment * factor}},
                    )
                )

        return candidates
