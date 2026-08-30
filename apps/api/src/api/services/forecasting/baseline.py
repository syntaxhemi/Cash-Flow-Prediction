from calendar import monthrange
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from database import IUnitOfWork
from database.models import (
    ForecastRunModel,
    ForecastRunPeriodModel,
    MonthlyCashflowAggregateModel,
)
from domain.exceptions import InvalidForecastRunError
from domain.forecasting import ForecastStatus
from ml import (
    ForecastFeaturePreparationService,
    ForecastInferenceService,
    ModelArtifactLoader,
)
from schemas.financial import StaticFinancialSnapshotSchema
from schemas.forecasting import (
    ForecastFilterParams,
    ForecastObservationDriverSchema,
    ForecastRequestSchema,
    ForecastRunCreateSchema,
    ForecastRunPeriodCreateSchema,
    ForecastRunPeriodSchema,
    ForecastRunSchema,
)

from api.core.pagination import OffsetPaginationSchema
from api.schemas.forecasts import ForecastListResponse


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

        response = self._run_schema(run)
        response.static_snapshot = StaticFinancialSnapshotSchema.model_validate(
            snapshot
        )
        response.periods = [
            self._period_schema(period, aggregates_by_start) for period in period_models
        ]
        return await self._add_derived_data(response)

    async def get(
        self, enterprise_id: UUID, forecast_run_id: UUID
    ) -> ForecastRunSchema:
        """Retrieve one forecast with its persisted inputs and observations.

        Args:
            enterprise_id: Owning enterprise identifier.
            forecast_run_id: Forecast-run identifier.

        Returns:
            Forecast metadata, input periods, static snapshot, expected cash
            movements, observation drivers, and generic observations.

        Raises:
            InvalidForecastRunError: If the forecast does not belong to the
                enterprise or its input data is unavailable.
        """
        await self._uow.enterprises.get_active_by_id_or_raise(enterprise_id)
        run = await self._uow.forecasts.get_by_id_with_inputs(
            enterprise_id, forecast_run_id
        )
        if run is None:
            raise InvalidForecastRunError(
                f'Forecast run "{forecast_run_id}" does not exist.'
            )
        return await self._enrich_response(run)

    async def list_forecasts(
        self, enterprise_id: UUID, filters: ForecastFilterParams
    ) -> ForecastListResponse:
        """List persisted forecast runs and their recorded input periods.

        Args:
            enterprise_id: Owning enterprise identifier.
            filters: Run filters and pagination parameters.

        Returns:
            Paginated forecast history for the dashboard.
        """
        await self._uow.enterprises.get_active_by_id_or_raise(enterprise_id)
        result = await self._uow.forecasts.list_for_enterprise(enterprise_id, filters)
        items = [await self._enrich_response(run) for run in result.items]
        return ForecastListResponse(
            items=items,
            pagination=OffsetPaginationSchema(
                limit=filters.limit,
                offset=filters.offset,
                total_count=result.total_count,
                has_next=filters.offset + len(items) < result.total_count,
                has_prev=filters.offset > 0,
            ),
        )

    @classmethod
    def _to_schema(cls, run: ForecastRunModel) -> ForecastRunSchema:
        """Convert a forecast model with loaded inputs to its response schema."""
        response = cls._run_schema(run)
        response.periods = [
            cls._period_schema(period)
            for period in sorted(run.periods, key=lambda item: item.sequence_index)
        ]
        return response

    async def _enrich_response(self, run: ForecastRunModel) -> ForecastRunSchema:
        """Add joined financial context and derived dashboard observations."""
        response = self._to_schema(run)
        if run.static_snapshot is not None:
            response.static_snapshot = StaticFinancialSnapshotSchema.model_validate(
                run.static_snapshot
            )

        return await self._add_derived_data(response)

    async def _add_derived_data(self, response: ForecastRunSchema) -> ForecastRunSchema:
        """Add expected cash movements and cautious forecast observations."""

        expected = await self._uow.financial_transactions.get_expected_cashflow(
            response.enterprise_id,
            response.target_period_start,
            response.target_period_end,
        )
        response.expected_inflows = expected.inflows
        response.expected_outflows = expected.outflows
        response.observation_drivers = self._observation_drivers(response)
        response.observations = self._observations(response)
        return response

    @staticmethod
    def _observation_drivers(
        run: ForecastRunSchema,
    ) -> list[ForecastObservationDriverSchema]:
        """Build the three most intuitive observed model-input drivers."""
        periods = run.periods
        return [
            ForecastObservationDriverSchema(
                label='Receivables',
                value=sum(
                    (period.total_invoice_amount for period in periods), Decimal()
                ),
                detail='Invoice value recorded across the six-month model window.',
            ),
            ForecastObservationDriverSchema(
                label='Collections',
                value=sum((period.total_inflows for period in periods), Decimal()),
                detail='Recorded inflows across the six-month model window.',
            ),
            ForecastObservationDriverSchema(
                label='Operating costs',
                value=sum((period.total_outflows for period in periods), Decimal()),
                detail='Recorded outflows across the six-month model window.',
            ),
        ]

    @staticmethod
    def _observations(run: ForecastRunSchema) -> list[str]:
        """Generate cautious, trend-based statements from persisted values."""
        observations = [
            (
                'The baseline remains above the solvency buffer for the selected '
                'period.'
                if run.buffer_gap >= 0
                else 'The baseline falls below the solvency buffer for the selected '
                'period.'
            )
        ]
        periods = run.periods
        if len(periods) >= 2:
            first, latest = periods[0], periods[-1]
            if latest.total_inflows > first.total_inflows:
                observations.append(
                    'Recorded inflows are trending upward across the model window.'
                )
            elif latest.total_inflows < first.total_inflows:
                observations.append(
                    'Recorded inflows are trending downward across the model window.'
                )
            if latest.total_outflows > first.total_outflows:
                observations.append(
                    'Recorded outflows are trending upward across the model window.'
                )
            elif latest.total_outflows < first.total_outflows:
                observations.append(
                    'Recorded outflows are easing across the model window.'
                )
        return observations

    @staticmethod
    def _run_schema(run: ForecastRunModel) -> ForecastRunSchema:
        """Convert forecast-run scalar fields without traversing input relations."""
        return ForecastRunSchema(
            id=run.id,
            enterprise_id=run.enterprise_id,
            run_type=run.run_type,
            target_period_start=run.target_period_start,
            target_period_end=run.target_period_end,
            sequence_window_months=run.sequence_window_months,
            static_snapshot_id=run.static_snapshot_id,
            model_version=run.model_version,
            artifact_version=run.artifact_version,
            predicted_net_cashflow=run.predicted_net_cashflow,
            solvency_buffer=run.solvency_buffer,
            buffer_gap=run.buffer_gap,
            status=run.status,
            requested_at=run.requested_at,
            completed_at=run.completed_at,
            created_at=run.created_at,
            periods=[],
        )

    @staticmethod
    def _period_schema(
        period: ForecastRunPeriodModel,
        aggregates_by_start: dict[date, MonthlyCashflowAggregateModel] | None = None,
    ) -> ForecastRunPeriodSchema:
        """Convert one persisted forecast period and aggregate to a response DTO."""
        aggregate = None
        if aggregates_by_start is not None:
            aggregate = next(
                (
                    item
                    for item in aggregates_by_start.values()
                    if item.id == period.monthly_cashflow_aggregate_id
                ),
                None,
            )
        else:
            aggregate = period.monthly_cashflow_aggregate
        if aggregate is None:
            raise InvalidForecastRunError(
                'Forecast period input data is unavailable for the selected run.'
            )
        return ForecastRunPeriodSchema(
            id=period.id,
            forecast_run_id=period.forecast_run_id,
            monthly_cashflow_aggregate_id=aggregate.id,
            sequence_index=period.sequence_index,
            period_start=aggregate.period_start,
            period_end=aggregate.period_end,
            total_invoice_amount=aggregate.total_invoice_amount,
            total_inflows=aggregate.total_inflows,
            total_outflows=aggregate.total_outflows,
            monthly_repayment=aggregate.monthly_repayment,
            total_payment_delay_days=aggregate.total_payment_delay_days,
            invoice_count=aggregate.invoice_count,
            payment_count=aggregate.payment_count,
            net_cashflow=aggregate.total_inflows - aggregate.total_outflows,
        )

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
        """Validate that the target range is ordered."""
        if period_end < period_start:
            raise InvalidForecastRunError(
                'Forecast target end cannot precede the target start.'
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
