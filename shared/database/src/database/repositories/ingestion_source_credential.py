from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.exceptions import IngestionSourceCredentialNotFoundError
from domain.ingestion import CredentialStatus
from schemas.ingestion import (
    IngestionSourceCredentialCreateSchema,
    IngestionSourceCredentialFilterParams,
    IngestionSourceCredentialUpdateSchema,
)
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from database.models import IngestionSourceCredentialModel


@dataclass(slots=True)
class IngestionSourceCredentialListResult:
    """Paginated ingestion-source credential query result."""

    items: list[IngestionSourceCredentialModel]
    total_count: int


class IngestionSourceCredentialRepository:
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
        payload: IngestionSourceCredentialCreateSchema,
        *,
        status: CredentialStatus,
        last_rotated_at: datetime,
    ) -> IngestionSourceCredentialModel:
        """Create and persist an ingestion-source credential.

        Args:
            enterprise_id: Owning enterprise identifier.
            ingestion_source_id: Owning ingestion-source identifier.
            payload: Credential creation data.
            status: Initial credential status.
            last_rotated_at: Initial credential rotation timestamp.

        Returns:
            The persisted credential model.
        """
        credential = IngestionSourceCredentialModel(
            enterprise_id=enterprise_id,
            ingestion_source_id=ingestion_source_id,
            status=status,
            last_rotated_at=last_rotated_at,
            **payload.model_dump(),
        )
        self._session.add(credential)
        await self._session.flush()
        await self._session.refresh(credential)
        return credential

    async def get_by_id(
        self, credential_id: UUID
    ) -> IngestionSourceCredentialModel | None:
        """Return an ingestion-source credential by identifier when it exists.

        Args:
            credential_id: Credential identifier to query.

        Returns:
            The matching credential model, or ``None``.
        """
        result = await self._session.execute(
            select(IngestionSourceCredentialModel).where(
                IngestionSourceCredentialModel.id == credential_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(
        self, credential_id: UUID
    ) -> IngestionSourceCredentialModel:
        """Return an ingestion-source credential or raise when missing.

        Args:
            credential_id: Credential identifier to query.

        Returns:
            The matching credential model.

        Raises:
            IngestionSourceCredentialNotFoundError: If no credential exists.
        """
        credential = await self.get_by_id(credential_id)
        if credential is None:
            raise IngestionSourceCredentialNotFoundError(
                f'Ingestion source credential "{credential_id}" does not exist.'
            )
        return credential

    async def get_active_for_source(
        self, ingestion_source_id: UUID
    ) -> IngestionSourceCredentialModel:
        """Return the newest active credential for an ingestion source.

        Args:
            ingestion_source_id: Owning ingestion-source identifier.

        Returns:
            The newest active credential model.

        Raises:
            IngestionSourceCredentialNotFoundError: If no active credential exists.
        """
        result = await self._session.execute(
            select(IngestionSourceCredentialModel)
            .where(
                IngestionSourceCredentialModel.ingestion_source_id
                == ingestion_source_id,
                IngestionSourceCredentialModel.status == CredentialStatus.ACTIVE,
            )
            .order_by(
                IngestionSourceCredentialModel.created_at.desc(),
                IngestionSourceCredentialModel.id,
            )
            .limit(1)
        )
        credential = result.scalar_one_or_none()
        if credential is None:
            raise IngestionSourceCredentialNotFoundError(
                f'No active credential exists for ingestion source "{ingestion_source_id}".'
            )
        return credential

    async def list_for_source(
        self,
        ingestion_source_id: UUID,
        filters: IngestionSourceCredentialFilterParams,
    ) -> IngestionSourceCredentialListResult:
        """Return paginated credentials for an ingestion source.

        Args:
            ingestion_source_id: Owning ingestion-source identifier.
            filters: Credential filters and offset pagination parameters.

        Returns:
            Matching credential models and filtered total count.
        """
        statement = select(IngestionSourceCredentialModel).where(
            IngestionSourceCredentialModel.ingestion_source_id == ingestion_source_id
        )
        count_statement = (
            select(func.count())
            .select_from(IngestionSourceCredentialModel)
            .where(
                IngestionSourceCredentialModel.ingestion_source_id
                == ingestion_source_id
            )
        )

        if filters.credential_type is not None:
            condition: ColumnElement[bool] = (
                IngestionSourceCredentialModel.credential_type
                == filters.credential_type
            )
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)

        if filters.status is not None:
            condition = IngestionSourceCredentialModel.status == filters.status
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)

        rows = await self._session.execute(
            statement.order_by(
                IngestionSourceCredentialModel.created_at,
                IngestionSourceCredentialModel.id,
            )
            .limit(filters.limit)
            .offset(filters.offset)
        )
        total_count = (await self._session.execute(count_statement)).scalar_one()
        return IngestionSourceCredentialListResult(
            items=list(rows.scalars().all()), total_count=total_count
        )

    async def update(
        self, credential_id: UUID, payload: IngestionSourceCredentialUpdateSchema
    ) -> IngestionSourceCredentialModel:
        """Update an existing ingestion-source credential.

        Args:
            credential_id: Credential identifier to update.
            payload: Validated credential persistence changes.

        Returns:
            The updated credential model.
        """
        credential = await self.get_by_id_or_raise(credential_id)

        for field_name, field_value in payload.model_dump(exclude_unset=True).items():
            setattr(credential, field_name, field_value)

        await self._session.flush()
        await self._session.refresh(credential)
        return credential
