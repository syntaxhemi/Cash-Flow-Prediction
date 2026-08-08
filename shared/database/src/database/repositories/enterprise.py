from dataclasses import dataclass
from typing import Any
from uuid import UUID

from domain.exceptions import EnterpriseAlreadyExistsError, EnterpriseNotFoundError
from schemas.enterprise import (
    EnterpriseCreateSchema,
    EnterpriseFilterParams,
    EnterpriseUpdateSchema,
)
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from database.models import EnterpriseModel


@dataclass(slots=True)
class EnterpriseListResult:
    """Paginated enterprise query result."""

    items: list[EnterpriseModel]
    total_count: int


class EnterpriseRepository:
    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an async database session.

        Args:
            session: Session used for persistence operations.
        """
        self._session = session

    async def create(self, payload: EnterpriseCreateSchema) -> EnterpriseModel:
        """Create and persist an enterprise.

        Args:
            payload: Validated enterprise creation data.

        Returns:
            The persisted enterprise model.

        Raises:
            EnterpriseAlreadyExistsError: If the external key is already used.
        """
        enterprise = EnterpriseModel(**payload.model_dump())
        self._session.add(enterprise)
        try:
            await self._session.flush()
        except IntegrityError as error:
            if self._matches_constraint(error, 'uq_enterprises_external_key'):
                raise EnterpriseAlreadyExistsError(
                    f'Enterprise with external key "{payload.external_key}" already exists.'
                ) from error
            raise
        await self._session.refresh(enterprise)
        return enterprise

    async def get_by_id(self, enterprise_id: UUID) -> EnterpriseModel | None:
        """Return an enterprise by identifier when it exists.

        Args:
            enterprise_id: Enterprise identifier to query.

        Returns:
            The matching model, or ``None``.
        """
        result = await self._session.execute(
            select(EnterpriseModel).where(EnterpriseModel.id == enterprise_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(self, enterprise_id: UUID) -> EnterpriseModel:
        """Return an enterprise or raise when it does not exist.

        Args:
            enterprise_id: Enterprise identifier to query.

        Returns:
            The matching enterprise model.

        Raises:
            EnterpriseNotFoundError: If no matching enterprise exists.
        """
        enterprise = await self.get_by_id(enterprise_id)
        if enterprise is None:
            raise EnterpriseNotFoundError(
                f'Enterprise "{enterprise_id}" does not exist.'
            )
        return enterprise

    async def get_active_by_id_or_raise(self, enterprise_id: UUID) -> EnterpriseModel:
        """Return an active enterprise or raise when it is missing or inactive.

        Args:
            enterprise_id: Enterprise identifier to query.

        Returns:
            The active enterprise model.

        Raises:
            EnterpriseNotFoundError: If no active enterprise exists.
        """
        enterprise = await self.get_by_id_or_raise(enterprise_id)
        if not enterprise.is_active:
            raise EnterpriseNotFoundError(
                f'Enterprise "{enterprise_id}" does not exist.'
            )
        return enterprise

    async def list(self, filters: EnterpriseFilterParams) -> EnterpriseListResult:
        """Return a paginated enterprise list.

        Args:
            filters: Enterprise filters and offset pagination parameters.

        Returns:
            Matching enterprise models and filtered total count.
        """
        statement: Any = select(EnterpriseModel)
        count_statement: Any = select(func.count()).select_from(EnterpriseModel)
        if filters.external_key is not None:
            condition: ColumnElement[bool] = EnterpriseModel.external_key.ilike(
                f'%{filters.external_key}%'
            )
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)
        if filters.legal_name is not None:
            condition = EnterpriseModel.legal_name.ilike(f'%{filters.legal_name}%')
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)
        condition = EnterpriseModel.is_active == filters.is_active
        statement = statement.where(condition)
        count_statement = count_statement.where(condition)
        rows = await self._session.execute(
            statement.order_by(EnterpriseModel.legal_name, EnterpriseModel.id)
            .limit(filters.limit)
            .offset(filters.offset)
        )
        total_count = (await self._session.execute(count_statement)).scalar_one()
        return EnterpriseListResult(
            items=list(rows.scalars().all()), total_count=total_count
        )

    async def update(
        self, enterprise_id: UUID, payload: EnterpriseUpdateSchema
    ) -> EnterpriseModel:
        """Update an existing enterprise.

        Args:
            enterprise_id: Enterprise identifier to update.
            payload: Validated fields to change.

        Returns:
            The updated enterprise model.

        Raises:
            EnterpriseNotFoundError: If no matching enterprise exists.
        """
        enterprise = await self.get_by_id_or_raise(enterprise_id)
        for field_name, field_value in payload.model_dump(exclude_unset=True).items():
            setattr(enterprise, field_name, field_value)
        await self._session.flush()
        await self._session.refresh(enterprise)
        return enterprise

    @staticmethod
    def _matches_constraint(error: IntegrityError, constraint_name: str) -> bool:
        """Check whether an integrity error names a constraint."""
        return constraint_name in str(error.orig)
