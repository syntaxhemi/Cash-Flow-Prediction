from uuid import UUID

from database import IUnitOfWork
from database.models import IngestionSourceModel
from domain.exceptions import (
    IngestionRunNotFoundError,
    IngestionSourceNotFoundError,
    InvalidIngestionRunError,
)
from domain.ingestion import IngestionRunType, IngestionStatus
from event_broker import IEventBrokerManager
from fastapi import UploadFile
from schemas.ingestion import (
    IngestionRunCreateSchema,
    IngestionRunFilterParams,
    IngestionRunSchema,
)

from api.core.pagination import OffsetPaginationSchema
from api.schemas.ingestion_runs import IngestionRunListResponse
from api.services.ingestion.uploads import UploadStagingService


class IngestionRunService:
    def __init__(
        self,
        uow: IUnitOfWork,
        event_broker_manager: IEventBrokerManager,
        stream_name: str,
        upload_staging_service: UploadStagingService,
    ) -> None:
        """Initialize ingestion-run application operations.

        Args:
            uow: Unit of work used for persistence.
            event_broker_manager: Shared Redis Streams manager.
            stream_name: Stream used for synchronization commands.
            upload_staging_service: Service used to stage file uploads.
        """
        self._uow = uow
        self._event_broker_manager = event_broker_manager
        self._stream_name = stream_name
        self._upload_staging_service = upload_staging_service

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

    async def create_upload(
        self,
        enterprise_id: UUID,
        source_id: UUID,
        upload: UploadFile,
        sheet_name: str | None = None,
    ) -> IngestionRunSchema:
        """Stage and dispatch an asynchronous CSV or Excel upload.

        Args:
            enterprise_id: Expected owning enterprise identifier.
            source_id: Owning file-ingestion source identifier.
            upload: Multipart CSV or XLSX upload.
            sheet_name: Optional worksheet name for XLSX uploads.

        Returns:
            The created pending upload ingestion-run schema.

        Raises:
            InvalidIngestionRunError: If the source is not a file source.
        """
        source = await self._validate_source(enterprise_id, source_id)
        if source.source_key not in {'csv', 'excel'}:
            raise InvalidIngestionRunError(
                f'Ingestion source "{source.source_key}" does not accept file uploads.'
            )

        staged_upload = await self._upload_staging_service.stage(
            upload, source.source_key, sheet_name
        )
        run = await self._uow.ingestion_runs.create(
            enterprise_id,
            source.id,
            IngestionRunCreateSchema(
                run_type=IngestionRunType.UPLOAD,
                status=IngestionStatus.PENDING,
            ),
        )
        await self._uow.ingestion_uploads.create(run.id, staged_upload)
        await self._uow.commit()

        await self._event_broker_manager.publish(
            self._stream_name,
            {
                'run_id': str(run.id),
                'enterprise_id': str(enterprise_id),
                'ingestion_source_id': str(source.id),
            },
        )
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
