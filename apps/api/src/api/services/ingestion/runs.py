from uuid import UUID

from database import IUnitOfWork
from database.models import IngestionSourceModel
from domain.exceptions import IngestionRunNotFoundError, IngestionSourceNotFoundError
from event_broker import IEventBrokerManager
from schemas.ingestion import (
    IngestionRunCreateSchema,
    IngestionRunFilterParams,
    IngestionRunSchema,
)

from api.core.pagination import OffsetPaginationSchema
from api.schemas.ingestion_runs import IngestionRunListResponse


class IngestionRunService:
    def __init__(
        self,
        uow: IUnitOfWork,
        event_broker_manager: IEventBrokerManager,
        stream_name: str,
    ) -> None:
        """Initialize ingestion-run application operations.

        Args:
            uow: Unit of work used for persistence.
            event_broker_manager: Shared Redis Streams manager.
            stream_name: Stream used for synchronization commands.
        """
        self._uow = uow
        self._event_broker_manager = event_broker_manager
        self._stream_name = stream_name

    async def create(
        self,
        enterprise_id: UUID,
        source_id: UUID,
        payload: IngestionRunCreateSchema,
    ) -> IngestionRunSchema:
        """Create and dispatch an ingestion synchronization run.

        Args:
            enterprise_id: Expected owning enterprise identifier.
            source_id: Owning ingestion-source identifier.
            payload: Synchronization request data.

        Returns:
            The created pending ingestion-run schema.
        """
        source = await self._validate_source(enterprise_id, source_id)

        await self._uow.ingestion_source_credentials.get_active_for_source(source.id)
        run = await self._uow.ingestion_runs.create(enterprise_id, source.id, payload)
        await self._uow.commit()

        fields = {
            'run_id': str(run.id),
            'enterprise_id': str(enterprise_id),
            'ingestion_source_id': str(source.id),
        }
        if payload.since is not None:
            fields['since'] = payload.since.isoformat()

        await self._event_broker_manager.publish(self._stream_name, fields)
        return IngestionRunSchema.model_validate(run)

    async def list(
        self,
        enterprise_id: UUID,
        source_id: UUID,
        filters: IngestionRunFilterParams,
    ) -> IngestionRunListResponse:
        """List synchronization runs for an ingestion source.

        Args:
            enterprise_id: Expected owning enterprise identifier.
            source_id: Owning ingestion-source identifier.
            filters: Run filters and pagination parameters.

        Returns:
            Paginated ingestion-run response.
        """
        await self._validate_source(enterprise_id, source_id)
        result = await self._uow.ingestion_runs.list_for_source(
            enterprise_id, source_id, filters
        )
        items = [IngestionRunSchema.model_validate(model) for model in result.items]
        return IngestionRunListResponse(
            items=items,
            pagination=OffsetPaginationSchema(
                limit=filters.limit,
                offset=filters.offset,
                total_count=result.total_count,
                has_next=filters.offset + len(items) < result.total_count,
                has_prev=filters.offset > 0,
            ),
        )

    async def get(
        self, enterprise_id: UUID, source_id: UUID, run_id: UUID
    ) -> IngestionRunSchema:
        """Return a synchronization run belonging to an ingestion source.

        Args:
            enterprise_id: Expected owning enterprise identifier.
            source_id: Expected owning ingestion-source identifier.
            run_id: Ingestion-run identifier to retrieve.

        Returns:
            The ingestion-run response schema.
        """
        await self._validate_source(enterprise_id, source_id)
        run = await self._uow.ingestion_runs.get_by_id_or_raise(run_id)
        if run.enterprise_id != enterprise_id or run.ingestion_source_id != source_id:
            raise IngestionRunNotFoundError(
                f'Ingestion run "{run_id}" does not belong to ingestion source.'
            )
        return IngestionRunSchema.model_validate(run)

    async def _validate_source(
        self, enterprise_id: UUID, source_id: UUID
    ) -> IngestionSourceModel:
        """Validate that an active source belongs to an active enterprise.

        Args:
            enterprise_id: Expected owning enterprise identifier.
            source_id: Source identifier to validate.

        Returns:
            The active ingestion-source model.
        """
        await self._uow.enterprises.get_active_by_id_or_raise(enterprise_id)
        source = await self._uow.ingestion_sources.get_active_by_id_or_raise(source_id)
        if source.enterprise_id != enterprise_id:
            raise IngestionSourceNotFoundError(
                f'Ingestion source "{source_id}" does not belong to enterprise.'
            )
        return source
