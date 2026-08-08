from dataclasses import dataclass
from typing import Any
from uuid import UUID

from domain.exceptions import (
    IngestionSourceAlreadyExistsError,
    IngestionSourceNotFoundError,
)
from schemas.ingestion import (
    IngestionSourceCreateSchema,
    IngestionSourceFilterParams,
    IngestionSourceUpdateSchema,
)
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from database.models import IngestionSourceModel


@dataclass(slots=True)
class IngestionSourceListResult:
    """Paginated ingestion-source query result."""

    items: list[IngestionSourceModel]
    total_count: int


class IngestionSourceRepository:
    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an async database session.

        Args:
            session: Session used for persistence operations.
        """
        self._session = session

    async def create(
        self, enterprise_id: UUID, payload: IngestionSourceCreateSchema
    ) -> IngestionSourceModel:
        """Create and persist an ingestion source for an enterprise.

        Args:
            enterprise_id: Owning enterprise identifier.
            payload: Validated source configuration.

        Returns:
            The persisted ingestion source model.

        Raises:
            IngestionSourceAlreadyExistsError: If the source key is duplicated.
        """
        source = IngestionSourceModel(
            enterprise_id=enterprise_id, **payload.model_dump()
        )
        self._session.add(source)
        try:
            await self._session.flush()
        except IntegrityError as error:
            if self._matches_constraint(error, 'uq_ingestion_sources_enterprise_id'):
                raise IngestionSourceAlreadyExistsError(
                    f'Source key "{payload.source_key}" already exists for enterprise.'
                ) from error
            raise
        await self._session.refresh(source)
        return source

    async def get_by_id(self, source_id: UUID) -> IngestionSourceModel | None:
        """Return an ingestion source by identifier when it exists."""
        result = await self._session.execute(
            select(IngestionSourceModel).where(IngestionSourceModel.id == source_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(self, source_id: UUID) -> IngestionSourceModel:
        """Return an ingestion source or raise when it is missing.

        Raises:
            IngestionSourceNotFoundError: If no matching source exists.
        """
        source = await self.get_by_id(source_id)
        if source is None:
            raise IngestionSourceNotFoundError(
                f'Ingestion source "{source_id}" does not exist.'
            )
        return source

    async def get_active_by_id_or_raise(self, source_id: UUID) -> IngestionSourceModel:
        """Return an active ingestion source or raise when it is unavailable.

        Args:
            source_id: Source identifier to query.

        Returns:
            The active ingestion source model.

        Raises:
            IngestionSourceNotFoundError: If no active source exists.
        """
        source = await self.get_by_id_or_raise(source_id)
        if not source.is_active:
            raise IngestionSourceNotFoundError(
                f'Ingestion source "{source_id}" does not exist.'
            )
        return source

    async def list_for_enterprise(
        self, enterprise_id: UUID, filters: IngestionSourceFilterParams
    ) -> IngestionSourceListResult:
        """Return a paginated source list for an enterprise.

        Args:
            enterprise_id: Owning enterprise identifier.
            filters: Source filters and offset pagination parameters.

        Returns:
            Matching source models and filtered total count.
        """
        statement: Any = select(IngestionSourceModel).where(
            IngestionSourceModel.enterprise_id == enterprise_id
        )
        count_statement: Any = (
            select(func.count())
            .select_from(IngestionSourceModel)
            .where(IngestionSourceModel.enterprise_id == enterprise_id)
        )
        if filters.source_key is not None:
            condition: ColumnElement[bool] = IngestionSourceModel.source_key.ilike(
                f'%{filters.source_key}%'
            )
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)
        if filters.status is not None:
            condition = IngestionSourceModel.status == filters.status
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)
        condition = IngestionSourceModel.is_active == filters.is_active
        statement = statement.where(condition)
        count_statement = count_statement.where(condition)
        rows = await self._session.execute(
            statement.order_by(
                IngestionSourceModel.display_name, IngestionSourceModel.id
            )
            .limit(filters.limit)
            .offset(filters.offset)
        )
        total_count = (await self._session.execute(count_statement)).scalar_one()
        return IngestionSourceListResult(
            items=list(rows.scalars().all()), total_count=total_count
        )

    async def update(
        self, source_id: UUID, payload: IngestionSourceUpdateSchema
    ) -> IngestionSourceModel:
        """Update an existing ingestion source.

        Args:
            source_id: Source identifier to update.
            payload: Validated fields to change.

        Returns:
            The updated source model.
        """
        source = await self.get_by_id_or_raise(source_id)
        for field_name, field_value in payload.model_dump(exclude_unset=True).items():
            setattr(source, field_name, field_value)
        await self._session.flush()
        await self._session.refresh(source)
        return source

    @staticmethod
    def _matches_constraint(error: IntegrityError, constraint_name: str) -> bool:
        """Check whether an integrity error names a constraint."""
        return constraint_name in str(error.orig)
