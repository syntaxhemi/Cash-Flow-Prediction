from dataclasses import dataclass
from typing import Any
from uuid import UUID

from domain.exceptions import InvalidForecastRunError
from schemas.forecasting import (
    ForecastFilterParams,
    ForecastRunCreateSchema,
    ForecastRunPeriodCreateSchema,
)
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import (
    ForecastRunModel,
    ForecastRunPeriodModel,
    StaticFinancialSnapshotModel,
)


@dataclass(slots=True)
class ForecastListResult:
    """Paginated forecast query result."""

    items: list[ForecastRunModel]
    total_count: int


class ForecastRepository:
    """Persist forecast executions and their selected input periods."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the forecast repository.

        Args:
            session: Async database session used for persistence.
        """
        self._session = session

    async def create(
        self,
        payload: ForecastRunCreateSchema,
    ) -> ForecastRunModel:
        """Create one completed forecast run with an exact request timestamp.

        Args:
            payload: Complete validated forecast persistence payload.

        Returns:
            The persisted completed forecast run.
        """
        run = ForecastRunModel(**payload.model_dump())
        self._session.add(run)

        try:
            await self._session.flush()

        except IntegrityError as error:
            raise InvalidForecastRunError(
                'Unable to create the forecast run due to a database constraint.'
            ) from error

        await self._session.refresh(run)
        return run

    async def create_periods(
        self,
        forecast_run_id: UUID,
        payloads: list[ForecastRunPeriodCreateSchema],
    ) -> list[ForecastRunPeriodModel]:
        """Persist the aggregate periods used by a forecast run.

        Args:
            forecast_run_id: Parent forecast run identifier.
            payloads: Ordered aggregate references.

        Returns:
            Persisted forecast period records.

        """
        periods = [
            ForecastRunPeriodModel(
                forecast_run_id=forecast_run_id,
                **payload.model_dump(),
            )
            for payload in payloads
        ]
        self._session.add_all(periods)

        try:
            await self._session.flush()

        except IntegrityError as error:
            raise InvalidForecastRunError(
                'Unable to create forecast-run periods due to a database constraint.'
            ) from error

        for period in periods:
            await self._session.refresh(period)

        return periods

    async def get_by_id(self, forecast_run_id: UUID) -> ForecastRunModel | None:
        """Return a forecast run by identifier when it exists.

        Args:
            forecast_run_id: Forecast run identifier.

        Returns:
            The matching forecast run, or ``None``.
        """
        result = await self._session.execute(
            select(ForecastRunModel).where(ForecastRunModel.id == forecast_run_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_inputs(
        self, enterprise_id: UUID, forecast_run_id: UUID
    ) -> ForecastRunModel | None:
        """Return an enterprise-owned forecast with its model inputs loaded.

        Args:
            enterprise_id: Owning enterprise identifier.
            forecast_run_id: Forecast-run identifier.

        Returns:
            The matching forecast run with periods, aggregates, and static snapshot
            relationships eagerly loaded, or ``None``.
        """
        result = await self._session.execute(
            select(ForecastRunModel)
            .join(
                StaticFinancialSnapshotModel,
                ForecastRunModel.static_snapshot_id == StaticFinancialSnapshotModel.id,
            )
            .where(
                ForecastRunModel.id == forecast_run_id,
                ForecastRunModel.enterprise_id == enterprise_id,
                StaticFinancialSnapshotModel.enterprise_id == enterprise_id,
            )
            .options(
                selectinload(ForecastRunModel.periods).selectinload(
                    ForecastRunPeriodModel.monthly_cashflow_aggregate
                ),
                selectinload(ForecastRunModel.static_snapshot),
            )
        )
        return result.scalar_one_or_none()

    async def list_for_enterprise(
        self, enterprise_id: UUID, filters: ForecastFilterParams
    ) -> ForecastListResult:
        """List forecast runs for an enterprise newest first.

        Args:
            enterprise_id: Owning enterprise identifier.
            filters: Run filters and pagination parameters.

        Returns:
            Paginated forecast runs with their input periods loaded.
        """
        statement: Any = select(ForecastRunModel).where(
            ForecastRunModel.enterprise_id == enterprise_id
        )
        count_statement: Any = (
            select(func.count())
            .select_from(ForecastRunModel)
            .where(ForecastRunModel.enterprise_id == enterprise_id)
        )

        if filters.run_type is not None:
            condition = ForecastRunModel.run_type == filters.run_type
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)
        if filters.status is not None:
            condition = ForecastRunModel.status == filters.status
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)

        result = await self._session.execute(
            statement.options(
                selectinload(ForecastRunModel.periods).selectinload(
                    ForecastRunPeriodModel.monthly_cashflow_aggregate
                ),
                selectinload(ForecastRunModel.static_snapshot),
            )
            .order_by(ForecastRunModel.created_at.desc(), ForecastRunModel.id)
            .limit(filters.limit)
            .offset(filters.offset)
        )
        total_count = (await self._session.execute(count_statement)).scalar_one()
        return ForecastListResult(
            items=list(result.scalars().all()), total_count=total_count
        )
