from uuid import UUID

from domain.exceptions import InvalidForecastRunError
from schemas.forecasting import (
    ForecastRunCreateSchema,
    ForecastRunPeriodCreateSchema,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import ForecastRunModel, ForecastRunPeriodModel


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
        self, forecast_run_id: UUID
    ) -> ForecastRunModel | None:
        """Return a forecast run with its persisted model inputs loaded.

        Args:
            forecast_run_id: Forecast-run identifier.

        Returns:
            The matching forecast run with periods, aggregates, and static snapshot
            relationships eagerly loaded, or ``None``.
        """
        result = await self._session.execute(
            select(ForecastRunModel)
            .where(ForecastRunModel.id == forecast_run_id)
            .options(
                selectinload(ForecastRunModel.periods).selectinload(
                    ForecastRunPeriodModel.monthly_cashflow_aggregate
                ),
                selectinload(ForecastRunModel.static_snapshot),
            )
        )
        return result.scalar_one_or_none()

    async def list_for_enterprise(self, enterprise_id: UUID) -> list[ForecastRunModel]:
        """List forecast runs for an enterprise newest first.

        Args:
            enterprise_id: Owning enterprise identifier.

        Returns:
            Forecast runs ordered by creation time descending.
        """
        result = await self._session.execute(
            select(ForecastRunModel)
            .where(ForecastRunModel.enterprise_id == enterprise_id)
            .order_by(ForecastRunModel.created_at.desc())
        )
        return list(result.scalars().all())
