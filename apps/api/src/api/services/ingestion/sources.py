from datetime import UTC, datetime
from uuid import UUID

from database import IUnitOfWork
from domain.exceptions import IngestionSourceNotFoundError
from domain.ingestion.rules import DefaultIngestionRules
from schemas.ingestion import (
    IngestionSourceCreateSchema,
    IngestionSourceFilterParams,
    IngestionSourceSchema,
    IngestionSourceUpdateSchema,
)

from api.core.pagination import OffsetPaginationSchema
from api.schemas.ingestion_sources import IngestionSourceListResponse


class IngestionSourceService:
    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize ingestion-source application operations.

        Args:
            uow: Unit of work used for persistence.
        """
        self._uow = uow
        self._rules = DefaultIngestionRules()

    async def create(
        self, enterprise_id: UUID, payload: IngestionSourceCreateSchema
    ) -> IngestionSourceSchema:
        """Validate and create an ingestion source.

        Args:
            enterprise_id: Owning enterprise identifier.
            payload: Source creation data.

        Returns:
            The created source schema.
        """
        await self._uow.enterprises.get_by_id_or_raise(enterprise_id)
        self._rules.validate_source(payload.source_key, payload.display_name)
        model = await self._uow.ingestion_sources.create(enterprise_id, payload)
        await self._uow.commit()
        return IngestionSourceSchema.model_validate(model)

    async def list(
        self, enterprise_id: UUID, filters: IngestionSourceFilterParams
    ) -> IngestionSourceListResponse:
        """List sources configured for an enterprise.

        Args:
            enterprise_id: Owning enterprise identifier.
            filters: Source list filters.

        Returns:
            Paginated source response.
        """
        await self._uow.enterprises.get_by_id_or_raise(enterprise_id)
        models = await self._uow.ingestion_sources.list_for_enterprise(
            enterprise_id, filters
        )
        items = [IngestionSourceSchema.model_validate(model) for model in models.items]
        return IngestionSourceListResponse(
            items=items,
            pagination=OffsetPaginationSchema(
                limit=filters.limit,
                offset=filters.offset,
                total_count=models.total_count,
                has_next=filters.offset + len(items) < models.total_count,
                has_prev=filters.offset > 0,
            ),
        )

    async def get(self, enterprise_id: UUID, source_id: UUID) -> IngestionSourceSchema:
        """Return a source belonging to an enterprise.

        Args:
            enterprise_id: Expected owning enterprise identifier.
            source_id: Source identifier to retrieve.

        Returns:
            The source response schema.

        Raises:
            IngestionSourceNotFoundError: If the source is missing or belongs elsewhere.
        """
        model = await self._uow.ingestion_sources.get_active_by_id_or_raise(source_id)
        if model.enterprise_id != enterprise_id:
            await self._uow.enterprises.get_by_id_or_raise(enterprise_id)
            raise IngestionSourceNotFoundError(
                f'Ingestion source "{source_id}" does not belong to enterprise.'
            )
        return IngestionSourceSchema.model_validate(model)

    async def delete(self, enterprise_id: UUID, source_id: UUID) -> None:
        """Soft-delete an ingestion source belonging to an enterprise.

        Args:
            enterprise_id: Expected owning enterprise identifier.
            source_id: Source identifier to deactivate.

        Raises:
            IngestionSourceNotFoundError: If the source is missing or inactive.
        """
        await self.get(enterprise_id, source_id)
        await self._uow.ingestion_sources.update(
            source_id,
            IngestionSourceUpdateSchema(
                is_active=False,
                deleted_at=datetime.now(UTC),
            ),
        )
        await self._uow.commit()

    async def update(
        self,
        enterprise_id: UUID,
        source_id: UUID,
        payload: IngestionSourceUpdateSchema,
    ) -> IngestionSourceSchema:
        """Validate and update an enterprise ingestion source.

        Args:
            enterprise_id: Expected owning enterprise identifier.
            source_id: Source identifier to update.
            payload: Source fields to change.

        Returns:
            The updated source schema.
        """
        await self.get(enterprise_id, source_id)

        values = payload.model_dump(exclude_unset=True)
        if 'display_name' in values:
            self._rules.validate_source('configured-source', values['display_name'])

        model = await self._uow.ingestion_sources.update(source_id, payload)
        await self._uow.commit()
        return IngestionSourceSchema.model_validate(model)
