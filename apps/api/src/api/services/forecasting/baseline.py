from calendar import monthrange
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from database import IUnitOfWork
from database.models import MonthlyCashflowAggregateModel
from domain.exceptions import InvalidForecastRunError
from domain.forecasting import ForecastStatus
from ml import (
    ForecastFeaturePreparationService,
    ForecastInferenceService,
    ModelArtifactLoader,
)
from schemas.forecasting import (
    ForecastRequestSchema,
    ForecastRunCreateSchema,
    ForecastRunPeriodCreateSchema,
    ForecastRunPeriodSchema,
    ForecastRunSchema,
)


class BaselineForecastService:
    """Orchestrate baseline forecasting from persisted financial features."""

    sequence_window_months = 6

    def __init__(self, uow: IUnitOfWork, artifact_directory: str) -> None:
        """Initialize the baseline forecasting workflow.

        Args:
            uow: Unit of work used to query inputs and persist forecast runs.
            artifact_directory: Directory containing the selected model artifacts.
        """
        self._uow = uow
        self._artifact_loader = ModelArtifactLoader(Path(artifact_directory))
        self._feature_preparation = ForecastFeaturePreparationService()
        self._inference = ForecastInferenceService()

    async def create(
        self, enterprise_id: UUID, payload: ForecastRequestSchema
    ) -> ForecastRunSchema:
        """Run and persist one baseline forecast.

        Args:
            enterprise_id: Owning enterprise identifier.
            payload: Target month and solvency-buffer request.

        Returns:
            Completed forecast result and input-period audit records.

        Raises:
            InvalidForecastRunError: If the target range or six-month input window is
                not available.
        """
        await self._uow.enterprises.get_active_by_id_or_raise(enterprise_id)
        self._validate_target_period(
            payload.target_period_start, payload.target_period_end
        )
        periods = _previous_months(
            payload.target_period_start, self.sequence_window_months
        )

        aggregates = await self._uow.monthly_cashflow_aggregates.list_for_window(
            enterprise_id, periods[0][0], periods[-1][1]
        )
        aggregates_by_start = {
            aggregate.period_start: aggregate for aggregate in aggregates
        }

        if set(aggregates_by_start) != {period[0] for period in periods}:
            raise InvalidForecastRunError(
                'Exactly six complete monthly cash-flow aggregates are required '
                'before the target period.'
            )

        snapshot = await self._uow.static_financial_snapshots.get_latest_for_date(
            enterprise_id, payload.target_period_end
        )
        if snapshot is None:
            raise InvalidForecastRunError(
                'No static financial snapshot is available for the forecast target.'
            )

        artifacts = self._artifact_loader.load()
        temporal_rows = [
            {
                'total_invoice_amount': float(
                    aggregates_by_start[start].total_invoice_amount
                ),
                'payment_delay': float(
                    aggregates_by_start[start].total_payment_delay_days
                ),
                'monthly_repayment': float(
                    aggregates_by_start[start].monthly_repayment
                ),
                'total_inflows': float(aggregates_by_start[start].total_inflows),
                'total_outflows': float(aggregates_by_start[start].total_outflows),
            }
            for start, _ in periods
        ]
        static_values = {
            'capex': float(snapshot.capex or 0),
            'cogs': float(snapshot.cogs or 0),
            'current_assets': float(snapshot.current_assets or 0),
            'current_liabilities': float(snapshot.current_liabilities or 0),
            'fixed_assets': float(snapshot.fixed_assets or 0),
            'long_term_liabilities': float(snapshot.long_term_liabilities or 0),
            'credit_score': float(snapshot.credit_score or 0),
            'failure_score': float(snapshot.failure_score or 0),
            'debt_to_revenue_ratio': float(snapshot.debt_to_revenue_ratio or 0),
            'missed_payments_number': float(snapshot.missed_payments_number or 0),
        }
        features = self._feature_preparation.prepare(
            temporal_rows, static_values, artifacts.metadata
        )

        prediction = self._inference.predict(features, artifacts)
        predicted = Decimal(str(prediction.predicted_net_cashflow))

        buffer_gap = predicted - payload.solvency_buffer
        requested_at = datetime.now(UTC)

        run = await self._uow.forecasts.create(
            ForecastRunCreateSchema(
                enterprise_id=enterprise_id,
                run_type=payload.run_type,
                target_period_start=payload.target_period_start,
                target_period_end=payload.target_period_end,
                sequence_window_months=self.sequence_window_months,
                static_snapshot_id=snapshot.id,
                model_version=prediction.model_version,
                artifact_version=str(prediction.artifact_version),
                predicted_net_cashflow=predicted,
                solvency_buffer=payload.solvency_buffer,
                buffer_gap=buffer_gap,
                status=ForecastStatus.COMPLETED,
                requested_at=requested_at,
                completed_at=requested_at,
            )
        )
        period_models = await self._uow.forecasts.create_periods(
            run.id,
            self._build_period_payloads(
                periods,
                aggregates_by_start,
            ),
        )

        await self._uow.commit()

        response = ForecastRunSchema.model_validate(run)
        response.periods = [
            ForecastRunPeriodSchema.model_validate(period) for period in period_models
        ]
        return response

    @staticmethod
    def _build_period_payloads(
        periods: list[tuple[date, date]],
        aggregates_by_start: dict[date, MonthlyCashflowAggregateModel],
    ) -> list[ForecastRunPeriodCreateSchema]:
        """Build the contiguous six-period persistence payload.

        Args:
            periods: Chronologically ordered forecast input periods.
            aggregates_by_start: Aggregates keyed by period start date.

        Returns:
            Ordered forecast-run period payloads.

        Raises:
            InvalidForecastRunError: If the period sequence is not exactly six rows.
        """
        if len(periods) != BaselineForecastService.sequence_window_months:
            raise InvalidForecastRunError(
                'A baseline forecast requires exactly six sequence periods.'
            )

        return [
            ForecastRunPeriodCreateSchema(
                monthly_cashflow_aggregate_id=aggregates_by_start[start].id,
                sequence_index=index,
            )
            for index, (start, _) in enumerate(periods)
        ]

    @staticmethod
    def _validate_target_period(period_start: date, period_end: date) -> None:
        """Validate that the target range is one complete calendar month."""
        expected_end = period_start.replace(
            day=monthrange(period_start.year, period_start.month)[1]
        )

        if period_start.day != 1 or period_end != expected_end:
            raise InvalidForecastRunError(
                'Forecast target must start on the first day and end on the last '
                'day of one calendar month.'
            )


def _previous_months(target_start: date, count: int) -> list[tuple[date, date]]:
    """Return the preceding calendar month bounds in chronological order."""
    periods: list[tuple[date, date]] = []
    month_index = target_start.year * 12 + target_start.month - 1 - count

    for _ in range(count):
        year, zero_based_month = divmod(month_index, 12)
        month = zero_based_month + 1
        start = date(year, month, 1)
        end = date(year, month, monthrange(year, month)[1])

        periods.append((start, end))
        month_index += 1

    return periods
