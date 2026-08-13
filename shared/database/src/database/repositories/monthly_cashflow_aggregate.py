from datetime import date
from uuid import UUID

from domain.exceptions import (
    MonthlyCashflowAggregateAlreadyExistsError,
    MonthlyCashflowAggregateNotFoundError,
)
from schemas.financial import (
    MonthlyCashflowAggregateCreateSchema,
    MonthlyCashflowAggregateUpdateSchema,
)
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import MonthlyCashflowAggregateModel


class MonthlyCashflowAggregateRepository:
    """Persist materialized enterprise-month forecasting features."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.

        Args:
            session: Async database session used for persistence.
        """
        self._session = session

    async def upsert(
        self, payload: MonthlyCashflowAggregateCreateSchema
    ) -> MonthlyCashflowAggregateModel:
        """Insert or replace one enterprise-month aggregate.

        Args:
            payload: Forecast-ready aggregate values to persist.

        Returns:
            The inserted or updated aggregate.
        """
        values = payload.model_dump()
        insert_statement = insert(MonthlyCashflowAggregateModel).values(values)

        statement = insert_statement.on_conflict_do_update(
            constraint='uq_monthly_cashflow_aggregates_enterprise_id',
            set_={key: insert_statement.excluded[key] for key in values if key != 'id'},
        ).returning(MonthlyCashflowAggregateModel)

        result = await self._session.execute(statement)
        return result.scalar_one()

    async def create(
        self, payload: MonthlyCashflowAggregateCreateSchema
    ) -> MonthlyCashflowAggregateModel:
        """Create one monthly aggregate without upsert semantics.

        Args:
            payload: Aggregate values to persist.

        Returns:
            The persisted aggregate.
        """
        aggregate = MonthlyCashflowAggregateModel(**payload.model_dump())
        self._session.add(aggregate)

        try:
            await self._session.flush()

        except IntegrityError as error:
            if 'uq_monthly_cashflow_aggregates_enterprise_id' in str(error.orig):
                raise MonthlyCashflowAggregateAlreadyExistsError(
                    f'Enterprise "{payload.enterprise_id}" already has an aggregate '
                    f'for "{payload.period_start}" to "{payload.period_end}".'
                ) from error
            raise

        await self._session.refresh(aggregate)
        return aggregate

    async def get_by_id(
        self, aggregate_id: UUID
    ) -> MonthlyCashflowAggregateModel | None:
        """Return a monthly aggregate by identifier when it exists.

        Args:
            aggregate_id: Aggregate identifier.

        Returns:
            The matching aggregate, or ``None``.
        """
        result = await self._session.execute(
            select(MonthlyCashflowAggregateModel).where(
                MonthlyCashflowAggregateModel.id == aggregate_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(
        self, aggregate_id: UUID
    ) -> MonthlyCashflowAggregateModel:
        """Return an aggregate or raise when it is missing.

        Args:
            aggregate_id: Aggregate identifier.

        Returns:
            The matching aggregate.

        Raises:
            MonthlyCashflowAggregateNotFoundError: If no aggregate exists.
        """
        aggregate = await self.get_by_id(aggregate_id)
        if aggregate is None:
            raise MonthlyCashflowAggregateNotFoundError(
                f'Monthly cash-flow aggregate "{aggregate_id}" does not exist.'
            )
        return aggregate

    async def update(
        self,
        aggregate_id: UUID,
        payload: MonthlyCashflowAggregateUpdateSchema,
    ) -> MonthlyCashflowAggregateModel:
        """Update derived values for one monthly aggregate.

        Args:
            aggregate_id: Aggregate identifier.
            payload: Derived values to replace.

        Returns:
            The updated aggregate.

        Raises:
            MonthlyCashflowAggregateNotFoundError: If no aggregate exists.
        """
        aggregate = await self.get_by_id_or_raise(aggregate_id)

        for field_name, field_value in payload.model_dump().items():
            setattr(aggregate, field_name, field_value)

        await self._session.flush()
        await self._session.refresh(aggregate)
        return aggregate

    async def list_for_window(
        self, enterprise_id: UUID, period_start: date, period_end: date
    ) -> list[MonthlyCashflowAggregateModel]:
        """List enterprise-month aggregates within a date range.

        Args:
            enterprise_id: Owning enterprise identifier.
            period_start: Inclusive first period boundary.
            period_end: Inclusive last period boundary.

        Returns:
            Matching aggregates ordered chronologically.
        """
        result = await self._session.execute(
            select(MonthlyCashflowAggregateModel)
            .where(
                MonthlyCashflowAggregateModel.enterprise_id == enterprise_id,
                MonthlyCashflowAggregateModel.period_start >= period_start,
                MonthlyCashflowAggregateModel.period_end <= period_end,
            )
            .order_by(MonthlyCashflowAggregateModel.period_start)
        )
        return list(result.scalars().all())
