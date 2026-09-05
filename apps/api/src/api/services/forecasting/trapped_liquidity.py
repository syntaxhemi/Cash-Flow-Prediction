from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from database import IUnitOfWork
from database.models import (
    CounterpartyMonthlyReceivableModel,
    FinancialTransactionModel,
)
from domain.exceptions import InvalidForecastRunError, InvalidSimulationError
from domain.financial import TransactionStatus, TransactionType
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
            reference_date = datetime.now(UTC).date()

            for counterparty_id, aggregate, sequence_index in candidates:
                transactions = (
                    await self._uow.financial_transactions.list_for_counterparty(
                        enterprise_id, counterparty_id
                    )
                )
                baseline_delay = Decimal(
                    str(context.temporal_rows[sequence_index]['payment_delay'])
                )
                if payload.payment_delay_days is None:
                    overdue_delay = self._overdue_delay_days(
                        transactions, reference_date
                    )
                    simulated_delay = max(baseline_delay, overdue_delay)
                else:
                    simulated_delay = baseline_delay + payload.payment_delay_days
                delay_days = (
                    overdue_delay
                    if payload.payment_delay_days is None
                    else payload.payment_delay_days
                )
                baseline_inflows = Decimal(
                    str(context.temporal_rows[sequence_index]['total_inflows'])
                )
                invoice_amount = Decimal(
                    str(context.temporal_rows[sequence_index]['total_invoice_amount'])
                )
                simulated_inflows = self._simulated_inflows(
                    baseline_inflows,
                    invoice_amount,
                    aggregate.outstanding_amount,
                    delay_days,
                )
                evaluation = self._evaluator.evaluate(
                    context,
                    {},
                    artifacts,
                    temporal_patch={
                        sequence_index: {
                            'payment_delay': simulated_delay,
                            'total_inflows': simulated_inflows,
                        }
                    },
                )
                delta = (
                    context.baseline_prediction - evaluation.predicted_net_cashflow
                    if payload.payment_delay_days is None
                    else evaluation.delta_from_baseline
                )
                rankings.append(
                    (
                        counterparty_id,
                        aggregate.outstanding_amount,
                        delta,
                    )
                )

            rankings.sort(
                key=lambda ranking: (abs(ranking[2]), ranking[1]),
                reverse=True,
            )
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
                'run_purpose': (
                    'preview' if payload.payment_delay_days is not None else 'analysis'
                ),
                'top_counterparty_id': str(rankings[0][0]),
                'top_simulated_cashflow_delta': str(rankings[0][2]),
                'modeled_trapped_liquidity': str(
                    sum((max(delta, Decimal(0)) for _, _, delta in rankings), Decimal())
                ),
                'method': (
                    'modeled payment-delay counterfactual with bounded '
                    'within-month inflow realization'
                ),
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
    def _simulated_inflows(
        baseline_inflows: Decimal,
        invoice_amount: Decimal,
        outstanding_amount: Decimal,
        delay_days: Decimal,
    ) -> Decimal:
        """Estimate bounded within-month inflows after a payment delay."""
        at_risk_amount = min(outstanding_amount, invoice_amount)
        delay_fraction = min(Decimal(1), delay_days / Decimal(30))
        inflow_reduction = min(baseline_inflows, at_risk_amount * delay_fraction)
        return baseline_inflows - inflow_reduction

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
    def _overdue_delay_days(
        transactions: list[FinancialTransactionModel],
        reference_date: date,
    ) -> Decimal:
        """Calculate an amount-weighted delay for unpaid overdue invoices.

        Args:
            transactions: Counterparty transactions containing invoice records.
            reference_date: Date used to measure unpaid invoice lateness.

        Returns:
            Amount-weighted overdue days, or zero when no invoice is overdue.
        """
        overdue_records: list[tuple[int, Decimal]] = []
        for transaction in transactions:
            due_date = transaction.due_date
            if (
                transaction.transaction_type is not TransactionType.INVOICE
                or transaction.status
                in (TransactionStatus.SETTLED, TransactionStatus.CANCELLED)
                or due_date is None
                or due_date >= reference_date
            ):
                continue
            overdue_records.append(
                ((reference_date - due_date).days, transaction.amount)
            )
        if not overdue_records:
            return Decimal(0)

        total_amount = sum((amount for _, amount in overdue_records), Decimal())
        if total_amount <= 0:
            return Decimal(sum(days for days, _ in overdue_records)) / Decimal(
                len(overdue_records)
            )

        weighted_days = sum(
            (Decimal(days) * amount for days, amount in overdue_records),
            Decimal(),
        )
        return weighted_days / total_amount
