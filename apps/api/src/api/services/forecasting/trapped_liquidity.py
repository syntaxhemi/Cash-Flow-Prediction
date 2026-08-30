from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from database import IUnitOfWork
from database.models import CounterpartyMonthlyReceivableModel
from domain.exceptions import InvalidForecastRunError, InvalidSimulationError
from domain.forecasting import ForecastStatus
from domain.simulation import SimulationStatus, SimulationType
from ml import ModelArtifactLoader
from schemas.simulation import (
    ReceivablesRankingCreateSchema,
    ReceivablesRankingSchema,
    SimulationRunCreateSchema,
    SimulationRunSchema,
    SimulationRunUpdateSchema,
    TrappedLiquidityRequestSchema,
)

from api.services.forecasting.counterfactual import (
    CounterfactualEvaluator,
    build_counterfactual_context,
)


class TrappedLiquiditySimulationService:
    """Orchestrate and persist trapped-liquidity simulations."""

    def __init__(self, uow: IUnitOfWork, artifact_directory: str) -> None:
        """Initialize the trapped-liquidity simulation service.

        Args:
            uow: Unit of work used to load inputs and persist simulation outputs.
            artifact_directory: Directory containing the selected model artifacts.
        """
        self._uow = uow
        self._artifact_loader = ModelArtifactLoader(Path(artifact_directory))
        self._evaluator = CounterfactualEvaluator()

    async def create(
        self,
        enterprise_id: UUID,
        forecast_run_id: UUID,
        payload: TrappedLiquidityRequestSchema,
    ) -> SimulationRunSchema:
        """Create and execute one trapped-liquidity simulation.

        Args:
            enterprise_id: Owning enterprise identifier.
            forecast_run_id: Completed baseline forecast identifier.
            payload: Counterparty selection and result limit.

        Returns:
            The completed simulation run and persisted receivables rankings.

        Raises:
            InvalidForecastRunError: If the baseline forecast is missing, belongs to
                another enterprise, or is not completed.
            InvalidSimulationError: If the baseline inputs or receivables data cannot
                produce a supported counterfactual.
        """
        await self._uow.enterprises.get_active_by_id_or_raise(enterprise_id)

        forecast = await self._uow.forecasts.get_by_id_with_inputs(
            enterprise_id, forecast_run_id
        )
        if forecast is None or forecast.enterprise_id != enterprise_id:
            raise InvalidForecastRunError(
                f'Forecast run "{forecast_run_id}" does not belong to the enterprise.'
            )

        if forecast.status is not ForecastStatus.COMPLETED:
            raise InvalidForecastRunError(
                'Trapped liquidity simulation requires a completed baseline forecast.'
            )

        artifacts = self._artifact_loader.load()
        context = build_counterfactual_context(forecast, artifacts.metadata)
        periods = sorted(forecast.periods, key=lambda period: period.sequence_index)
        receivables = (
            await self._uow.counterparty_monthly_receivables.list_for_enterprise(
                enterprise_id,
                periods[0].monthly_cashflow_aggregate.period_start,
                periods[-1].monthly_cashflow_aggregate.period_end,
            )
        )
        period_indexes = {
            period.monthly_cashflow_aggregate.period_start: period.sequence_index
            for period in periods
        }
        candidates = self._select_candidates(receivables, payload, period_indexes)
        if not candidates:
            raise InvalidSimulationError(
                'No counterparty receivables are available for trapped-liquidity '
                'simulation.'
            )

        requested_at = datetime.now(UTC)
        run = await self._uow.simulation_runs.create(
            SimulationRunCreateSchema(
                enterprise_id=enterprise_id,
                forecast_run_id=forecast_run_id,
                simulation_type=SimulationType.TRAPPED_LIQUIDITY,
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
            rankings: list[tuple[UUID, Decimal, Decimal]] = []

            for counterparty_id, aggregate, sequence_index in candidates:
                delay_reduction = self._delay_reduction(aggregate)
                baseline_delay = Decimal(
                    str(context.temporal_rows[sequence_index]['payment_delay'])
                )
                simulated_delay = max(Decimal(0), baseline_delay - delay_reduction)
                evaluation = self._evaluator.evaluate(
                    context,
                    {},
                    artifacts,
                    temporal_patch={sequence_index: {'payment_delay': simulated_delay}},
                )
                rankings.append(
                    (
                        counterparty_id,
                        aggregate.outstanding_amount,
                        evaluation.delta_from_baseline,
                    )
                )

            rankings.sort(key=lambda ranking: ranking[2], reverse=True)
            ranking_models = []

            for position, (counterparty_id, outstanding, delta) in enumerate(
                rankings, start=1
            ):
                ranking_models.append(
                    await self._uow.receivables_rankings.create(
                        run.id,
                        ReceivablesRankingCreateSchema(
                            counterparty_id=counterparty_id,
                            rank_position=position,
                            baseline_outstanding_amount=outstanding,
                            simulated_cashflow_delta=delta,
                        ),
                    )
                )

            summary = {
                'baseline_prediction': str(context.baseline_prediction),
                'ranked_counterparties': len(ranking_models),
                'top_counterparty_id': str(rankings[0][0]),
                'top_simulated_cashflow_delta': str(rankings[0][2]),
                'method': 'modeled payment-delay reduction',
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

        ranking_models = await self._uow.receivables_rankings.list_for_run(run.id)
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
            receivables_rankings=[
                ReceivablesRankingSchema.model_validate(ranking)
                for ranking in ranking_models
            ],
        )

    @staticmethod
    def _select_candidates(
        receivables: list[CounterpartyMonthlyReceivableModel],
        payload: TrappedLiquidityRequestSchema,
        period_indexes: dict[date, int],
    ) -> list[tuple[UUID, CounterpartyMonthlyReceivableModel, int]]:
        """Select one representative receivable aggregate per counterparty.

        Args:
            receivables: Receivable aggregates within the forecast window.
            payload: Counterparty selection and result limit.

        Returns:
            Counterparty, representative aggregate, and sequence-index tuples.
        """
        requested = set(payload.counterparty_ids or [])
        grouped: dict[UUID, list[CounterpartyMonthlyReceivableModel]] = {}

        for aggregate in receivables:
            if requested and aggregate.counterparty_id not in requested:
                continue
            grouped.setdefault(aggregate.counterparty_id, []).append(aggregate)

        candidates = []

        for counterparty_id, rows in grouped.items():
            representative = max(
                rows,
                key=lambda row: (row.outstanding_amount, row.period_end),
            )
            sequence_index = period_indexes.get(representative.period_start)

            if sequence_index is not None:
                candidates.append((counterparty_id, representative, sequence_index))

        candidates.sort(key=lambda item: item[1].outstanding_amount, reverse=True)
        return candidates[: payload.max_counterparties]

    @staticmethod
    def _delay_reduction(
        aggregate: CounterpartyMonthlyReceivableModel,
    ) -> Decimal:
        """Estimate removable payment-delay contribution for one receivable.

        Args:
            aggregate: Counterparty monthly receivable aggregate.

        Returns:
            Modeled payment-delay reduction in days.
        """
        average_delay = aggregate.average_payment_delay_days or Decimal(0)
        late_count = aggregate.late_invoice_count or 0
        return average_delay * late_count if late_count else average_delay
