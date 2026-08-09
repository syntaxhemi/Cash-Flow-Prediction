from dataclasses import dataclass
from typing import Any
from uuid import UUID

from domain.exceptions import IngestionRunNotFoundError
from schemas.ingestion import (
    IngestionRunCreateSchema,
    IngestionRunFilterParams,
    IngestionRunUpdateSchema,
)
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from database.models import IngestionRunModel


@dataclass(slots=True)
class IngestionRunListResult:
    """Paginated ingestion-run query result."""

    items: list[IngestionRunModel]
    total_count: int


class IngestionRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an async database session.

        Args:
            session: Session used for persistence operations.
        """
        self._session = session

    async def create(
        self,
        enterprise_id: UUID,
        ingestion_source_id: UUID,
        payload: IngestionRunCreateSchema,
    ) -> IngestionRunModel:
        """Create and persist an ingestion run.

        Args:
            enterprise_id: Owning enterprise identifier.
            ingestion_source_id: Owning ingestion-source identifier.
            payload: Run creation data.

        Returns:
            The persisted pending run model.
        """
        run = IngestionRunModel(
            enterprise_id=enterprise_id,
            ingestion_source_id=ingestion_source_id,
            run_type=payload.run_type,
            status=payload.status,
        )
        self._session.add(run)
        await self._session.flush()
        await self._session.refresh(run)
        return run

    async def get_by_id(self, run_id: UUID) -> IngestionRunModel | None:
        """Return an ingestion run by identifier when it exists.

        Args:
            run_id: Ingestion-run identifier to query.

        Returns:
            The matching run model, or ``None``.
        """
        result = await self._session.execute(
            select(IngestionRunModel).where(IngestionRunModel.id == run_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(self, run_id: UUID) -> IngestionRunModel:
        """Return an ingestion run or raise when it is missing.

        Args:
            run_id: Ingestion-run identifier to query.

        Returns:
            The matching run model.

        Raises:
            IngestionRunNotFoundError: If no run exists.
        """
        run = await self.get_by_id(run_id)
        if run is None:
            raise IngestionRunNotFoundError(f'Ingestion run "{run_id}" does not exist.')
        return run

    async def list_for_source(
        self,
        enterprise_id: UUID,
        ingestion_source_id: UUID,
        filters: IngestionRunFilterParams,
    ) -> IngestionRunListResult:
        """Return paginated runs for an enterprise ingestion source.

        Args:
            enterprise_id: Owning enterprise identifier.
            ingestion_source_id: Owning ingestion-source identifier.
            filters: Run filters and pagination parameters.

        Returns:
            Matching run models and filtered total count.
        """
        statement: Any = select(IngestionRunModel).where(
            IngestionRunModel.enterprise_id == enterprise_id,
            IngestionRunModel.ingestion_source_id == ingestion_source_id,
        )
        count_statement: Any = (
            select(func.count())
            .select_from(IngestionRunModel)
            .where(
                IngestionRunModel.enterprise_id == enterprise_id,
                IngestionRunModel.ingestion_source_id == ingestion_source_id,
            )
        )

        if filters.status is not None:
            condition: ColumnElement[bool] = IngestionRunModel.status == filters.status
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)
        if filters.run_type is not None:
            condition = IngestionRunModel.run_type == filters.run_type
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)

        rows = await self._session.execute(
            statement.order_by(
                IngestionRunModel.created_at.desc(), IngestionRunModel.id
            )
            .limit(filters.limit)
            .offset(filters.offset)
        )
        total_count = (await self._session.execute(count_statement)).scalar_one()
        return IngestionRunListResult(
            items=list(rows.scalars().all()), total_count=total_count
        )

    async def update(
        self, run_id: UUID, payload: IngestionRunUpdateSchema
    ) -> IngestionRunModel:
        """Update an ingestion run.

        Args:
            run_id: Ingestion-run identifier to update.
            payload: Validated run state changes.

        Returns:
            The updated run model.

        Raises:
            IngestionRunNotFoundError: If no run exists.
        """
        run = await self.get_by_id_or_raise(run_id)

        for field_name, field_value in payload.model_dump(exclude_unset=True).items():
            setattr(run, field_name, field_value)

        await self._session.flush()
        await self._session.refresh(run)
        return run
