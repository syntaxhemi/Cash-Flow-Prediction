from datetime import date
from uuid import UUID

from domain.exceptions import (
    CounterpartyMonthlyReceivableAlreadyExistsError,
    CounterpartyMonthlyReceivableNotFoundError,
    InvalidFinancialRecordError,
)
from schemas.financial import (
    CounterpartyMonthlyReceivableCreateSchema,
    CounterpartyMonthlyReceivableUpdateSchema,
)
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import CounterpartyMonthlyReceivableModel


class CounterpartyMonthlyReceivableRepository:
    """Persist materialized counterparty receivable features."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.

        Args:
            session: Async database session used for persistence.
        """
        self._session = session

    async def upsert(
        self, payload: CounterpartyMonthlyReceivableCreateSchema
    ) -> CounterpartyMonthlyReceivableModel:
        """Insert or replace one counterparty-month aggregate.

        Args:
            payload: Aggregate values to persist.

        Returns:
            The inserted or updated aggregate.
        """
        values = payload.model_dump()
        insert_statement = insert(CounterpartyMonthlyReceivableModel).values(values)

        statement = insert_statement.on_conflict_do_update(
            constraint='uq_counterparty_monthly_receivables_enterprise_id',
            set_={key: insert_statement.excluded[key] for key in values if key != 'id'},
        ).returning(CounterpartyMonthlyReceivableModel)

        try:
            result = await self._session.execute(statement)
        except IntegrityError as error:
            raise InvalidFinancialRecordError(
                'Unable to upsert the counterparty receivable aggregate due to a '
                'database constraint.'
            ) from error
        return result.scalar_one()

    async def create(
        self, payload: CounterpartyMonthlyReceivableCreateSchema
    ) -> CounterpartyMonthlyReceivableModel:
        """Create one receivable aggregate without upsert semantics.

        Args:
            payload: Aggregate values to persist.

        Returns:
            The persisted aggregate.
        """
        aggregate = CounterpartyMonthlyReceivableModel(**payload.model_dump())
        self._session.add(aggregate)

        try:
            await self._session.flush()

        except IntegrityError as error:
            if 'uq_counterparty_monthly_receivables_enterprise_id' in str(error.orig):
                raise CounterpartyMonthlyReceivableAlreadyExistsError(
                    f'Counterparty "{payload.counterparty_id}" already has a '
                    f'receivable aggregate for "{payload.period_start}" to '
                    f'"{payload.period_end}".'
                ) from error
            raise InvalidFinancialRecordError(
                'Unable to create the counterparty receivable aggregate due to a '
                'database constraint.'
            ) from error

        await self._session.refresh(aggregate)
        return aggregate

    async def get_by_id(
        self, aggregate_id: UUID
    ) -> CounterpartyMonthlyReceivableModel | None:
        """Return a receivable aggregate by identifier when it exists.

        Args:
            aggregate_id: Aggregate identifier.

        Returns:
            The matching aggregate, or ``None``.
        """
        result = await self._session.execute(
            select(CounterpartyMonthlyReceivableModel).where(
                CounterpartyMonthlyReceivableModel.id == aggregate_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(
        self, aggregate_id: UUID
    ) -> CounterpartyMonthlyReceivableModel:
        """Return a receivable aggregate or raise when it is missing.

        Args:
            aggregate_id: Aggregate identifier.

        Returns:
            The matching aggregate.

        Raises:
            CounterpartyMonthlyReceivableNotFoundError: If no aggregate exists.
        """
        aggregate = await self.get_by_id(aggregate_id)
        if aggregate is None:
            raise CounterpartyMonthlyReceivableNotFoundError(
                f'Counterparty monthly receivable "{aggregate_id}" does not exist.'
            )
        return aggregate

    async def update(
        self,
        aggregate_id: UUID,
        payload: CounterpartyMonthlyReceivableUpdateSchema,
    ) -> CounterpartyMonthlyReceivableModel:
        """Update derived values for one receivable aggregate.

        Args:
            aggregate_id: Aggregate identifier.
            payload: Derived values to replace.

        Returns:
            The updated aggregate.

        Raises:
            CounterpartyMonthlyReceivableNotFoundError: If no aggregate exists.
        """
        aggregate = await self.get_by_id_or_raise(aggregate_id)

        for field_name, field_value in payload.model_dump().items():
            setattr(aggregate, field_name, field_value)

        try:
            await self._session.flush()
        except IntegrityError as error:
            raise InvalidFinancialRecordError(
                f'Unable to update counterparty receivable aggregate "{aggregate_id}" '
                'due to a database constraint.'
            ) from error
        await self._session.refresh(aggregate)
        return aggregate

    async def list_for_enterprise(
        self, enterprise_id: UUID, period_start: date, period_end: date
    ) -> list[CounterpartyMonthlyReceivableModel]:
        """List counterparty receivables within an enterprise date range.

        Args:
            enterprise_id: Owning enterprise identifier.
            period_start: Inclusive first period boundary.
            period_end: Inclusive last period boundary.

        Returns:
            Matching receivable aggregates ordered by period and outstanding amount.
        """
        result = await self._session.execute(
            select(CounterpartyMonthlyReceivableModel)
            .options(selectinload(CounterpartyMonthlyReceivableModel.counterparty))
            .where(
                CounterpartyMonthlyReceivableModel.enterprise_id == enterprise_id,
                CounterpartyMonthlyReceivableModel.period_start >= period_start,
                CounterpartyMonthlyReceivableModel.period_end <= period_end,
            )
            .order_by(
                CounterpartyMonthlyReceivableModel.period_start,
                CounterpartyMonthlyReceivableModel.outstanding_amount.desc(),
            )
        )
        return list(result.scalars().all())
