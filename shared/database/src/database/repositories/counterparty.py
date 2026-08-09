from dataclasses import dataclass
from typing import Any
from uuid import UUID

from domain.exceptions import (
    CounterpartyAlreadyExistsError,
    CounterpartyNotFoundError,
)
from schemas.financial import (
    CounterpartyCreateSchema,
    CounterpartyFilterParams,
    CounterpartyUpdateSchema,
)
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from database.models import CounterpartyModel


@dataclass(slots=True)
class CounterpartyListResult:
    """Paginated counterparty query result."""

    items: list[CounterpartyModel]
    total_count: int


class CounterpartyRepository:
    """Persist enterprise-scoped counterparty identities."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an async database session.

        Args:
            session: Session used for persistence operations.
        """
        self._session = session

    async def create(
        self,
        enterprise_id: UUID,
        payload: CounterpartyCreateSchema,
    ) -> CounterpartyModel:
        """Create and persist a counterparty.

        Args:
            enterprise_id: Owning enterprise identifier.
            payload: Validated counterparty creation data.

        Returns:
            The newly persisted counterparty model.

        Raises:
            CounterpartyAlreadyExistsError: If the external key is already used.
        """
        counterparty = CounterpartyModel(
            enterprise_id=enterprise_id, **payload.model_dump()
        )
        self._session.add(counterparty)

        try:
            await self._session.flush()

        except IntegrityError as error:
            if self._matches_constraint(
                error,
                'counterparties_enterprise_id_external_key_key',
                'uq_counterparties_enterprise_id_external_key',
            ):
                raise CounterpartyAlreadyExistsError(
                    f'Counterparty with external key "{payload.external_key}" '
                    f'already exists for enterprise "{enterprise_id}".'
                ) from error
            raise

        await self._session.refresh(counterparty)
        return counterparty

    async def get_by_id(self, counterparty_id: UUID) -> CounterpartyModel | None:
        """Return a counterparty by identifier when it exists.

        Args:
            counterparty_id: Counterparty identifier to query.

        Returns:
            The matching counterparty model, or ``None``.
        """
        result = await self._session.execute(
            select(CounterpartyModel).where(CounterpartyModel.id == counterparty_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(self, counterparty_id: UUID) -> CounterpartyModel:
        """Return a counterparty or raise when it is missing.

        Args:
            counterparty_id: Counterparty identifier to query.

        Returns:
            The matching counterparty model.

        Raises:
            CounterpartyNotFoundError: If no counterparty exists.
        """
        counterparty = await self.get_by_id(counterparty_id)
        if counterparty is None:
            raise CounterpartyNotFoundError(
                f'Counterparty "{counterparty_id}" does not exist.'
            )
        return counterparty

    async def get_by_external_key(
        self, enterprise_id: UUID, external_key: str
    ) -> CounterpartyModel | None:
        """Return a counterparty by enterprise-scoped external key.

        Args:
            enterprise_id: Owning enterprise identifier.
            external_key: Source-system identity to query.

        Returns:
            The matching counterparty model, or ``None``.
        """
        result = await self._session.execute(
            select(CounterpartyModel).where(
                CounterpartyModel.enterprise_id == enterprise_id,
                CounterpartyModel.external_key == external_key,
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self, enterprise_id: UUID, filters: CounterpartyFilterParams
    ) -> CounterpartyListResult:
        """Return a paginated counterparty list for an enterprise.

        Args:
            enterprise_id: Owning enterprise identifier.
            filters: Counterparty filters and pagination parameters.

        Returns:
            Matching counterparty models and total count.
        """
        statement: Any = select(CounterpartyModel).where(
            CounterpartyModel.enterprise_id == enterprise_id,
        )
        count_statement: Any = (
            select(func.count())
            .select_from(CounterpartyModel)
            .where(CounterpartyModel.enterprise_id == enterprise_id)
        )

        if filters.external_key is not None:
            condition = CounterpartyModel.external_key.ilike(
                f'%{filters.external_key}%'
            )
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)
        if filters.name is not None:
            condition = CounterpartyModel.name.ilike(f'%{filters.name}%')
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)

        active_condition: ColumnElement[bool] = (
            CounterpartyModel.is_active == filters.is_active
        )
        statement = statement.where(active_condition)
        count_statement = count_statement.where(active_condition)

        rows = await self._session.execute(
            statement.order_by(CounterpartyModel.name, CounterpartyModel.id)
            .limit(filters.limit)
            .offset(filters.offset)
        )
        total_count = (await self._session.execute(count_statement)).scalar_one()
        return CounterpartyListResult(
            items=list(rows.scalars().all()), total_count=total_count
        )

    async def update(
        self, counterparty_id: UUID, payload: CounterpartyUpdateSchema
    ) -> CounterpartyModel:
        """Update an existing counterparty.

        Args:
            counterparty_id: Counterparty identifier to update.
            payload: Validated counterparty fields to change.

        Returns:
            The updated counterparty model.

        Raises:
            CounterpartyNotFoundError: If no counterparty exists.
        """
        counterparty = await self.get_by_id_or_raise(counterparty_id)

        for field_name, field_value in payload.model_dump(exclude_unset=True).items():
            setattr(counterparty, field_name, field_value)

        await self._session.flush()
        await self._session.refresh(counterparty)
        return counterparty

    @staticmethod
    def _matches_constraint(error: IntegrityError, *constraint_names: str) -> bool:
        """Return whether an integrity error references a known constraint.

        Args:
            error: Integrity error raised by the database.
            *constraint_names: Constraint names to match.

        Returns:
            ``True`` when the database error references one of the constraints.
        """
        error_message = str(error.orig)
        return any(name in error_message for name in constraint_names)
