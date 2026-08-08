from datetime import UTC, datetime
from uuid import UUID

from database import IUnitOfWork
from database.models import IngestionSourceModel
from domain.exceptions import (
    IngestionSourceCredentialNotFoundError,
    InvalidIngestionSourceCredentialStateError,
)
from domain.ingestion import CredentialStatus
from schemas.ingestion import (
    IngestionSourceCredentialCreateSchema,
    IngestionSourceCredentialFilterParams,
    IngestionSourceCredentialMetadataUpdateSchema,
    IngestionSourceCredentialSchema,
    IngestionSourceCredentialSecretUpdateSchema,
    IngestionSourceCredentialUpdateSchema,
)

from api.core.pagination import OffsetPaginationSchema
from api.schemas.ingestion_credentials import IngestionSourceCredentialListResponse


class IngestionSourceCredentialService:
    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize ingestion-source credential operations.

        Args:
            uow: Unit of work used for persistence.
        """
        self._uow = uow

    async def create(
        self,
        enterprise_id: UUID,
        source_id: UUID,
        payload: IngestionSourceCredentialCreateSchema,
    ) -> IngestionSourceCredentialSchema:
        """Create a credential for an active ingestion source.

        Args:
            enterprise_id: Expected owning enterprise identifier.
            source_id: Owning ingestion-source identifier.
            payload: Credential creation data.

        Returns:
            The created credential metadata.
        """
        source = await self._get_source(enterprise_id, source_id)
        model = await self._uow.ingestion_source_credentials.create(
            enterprise_id,
            source.id,
            payload,
            status=CredentialStatus.ACTIVE,
            last_rotated_at=datetime.now(UTC),
        )
        await self._uow.commit()
        return IngestionSourceCredentialSchema.model_validate(model)

    async def list(
        self,
        enterprise_id: UUID,
        source_id: UUID,
        filters: IngestionSourceCredentialFilterParams,
    ) -> IngestionSourceCredentialListResponse:
        """List credentials configured for an active ingestion source.

        Args:
            enterprise_id: Expected owning enterprise identifier.
            source_id: Owning ingestion-source identifier.
            filters: Credential filters and pagination parameters.

        Returns:
            Paginated credential metadata response.
        """
        source = await self._get_source(enterprise_id, source_id)
        result = await self._uow.ingestion_source_credentials.list_for_source(
            source.id, filters
        )
        items = [
            IngestionSourceCredentialSchema.model_validate(model)
            for model in result.items
        ]
        return IngestionSourceCredentialListResponse(
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
        self, enterprise_id: UUID, source_id: UUID, credential_id: UUID
    ) -> IngestionSourceCredentialSchema:
        """Return credential metadata belonging to an ingestion source.

        Args:
            enterprise_id: Expected owning enterprise identifier.
            source_id: Expected owning ingestion-source identifier.
            credential_id: Credential identifier to retrieve.

        Returns:
            The credential metadata response.

        Raises:
            IngestionSourceCredentialNotFoundError: If ownership does not match.
        """
        await self._get_source(enterprise_id, source_id)
        model = await self._uow.ingestion_source_credentials.get_by_id_or_raise(
            credential_id
        )
        if model.ingestion_source_id != source_id:
            raise IngestionSourceCredentialNotFoundError(
                f'Ingestion source credential "{credential_id}" does not belong '
                'to ingestion source.'
            )
        return IngestionSourceCredentialSchema.model_validate(model)

    async def update(
        self,
        enterprise_id: UUID,
        source_id: UUID,
        credential_id: UUID,
        payload: IngestionSourceCredentialMetadataUpdateSchema,
    ) -> IngestionSourceCredentialSchema:
        """Update credential metadata without exposing its secret value.

        Args:
            enterprise_id: Expected owning enterprise identifier.
            source_id: Expected owning ingestion-source identifier.
            credential_id: Credential identifier to update.
            payload: Credential metadata changes.

        Returns:
            The updated credential metadata response.
        """
        await self.get(enterprise_id, source_id, credential_id)
        model = await self._uow.ingestion_source_credentials.update(
            credential_id,
            IngestionSourceCredentialUpdateSchema.model_validate(
                payload.model_dump(exclude_unset=True)
            ),
        )
        await self._uow.commit()
        return IngestionSourceCredentialSchema.model_validate(model)

    async def rotate(
        self,
        enterprise_id: UUID,
        source_id: UUID,
        credential_id: UUID,
        payload: IngestionSourceCredentialSecretUpdateSchema,
    ) -> IngestionSourceCredentialSchema:
        """Replace the stored credential value for an active credential.

        Args:
            enterprise_id: Expected owning enterprise identifier.
            source_id: Expected owning ingestion-source identifier.
            credential_id: Credential identifier to rotate.
            payload: Replacement credential value.

        Returns:
            The rotated credential metadata response.

        Raises:
            InvalidIngestionSourceCredentialStateError: If the credential is not active.
        """
        await self.get(enterprise_id, source_id, credential_id)
        current = await self._uow.ingestion_source_credentials.get_by_id_or_raise(
            credential_id
        )

        if current.status != CredentialStatus.ACTIVE:
            raise InvalidIngestionSourceCredentialStateError(
                'Only active ingestion-source credentials can be rotated.'
            )

        model = await self._uow.ingestion_source_credentials.update(
            credential_id,
            IngestionSourceCredentialUpdateSchema(
                secret_ref=payload.secret_ref,
                status=CredentialStatus.ACTIVE,
                last_rotated_at=datetime.now(UTC),
            ),
        )
        await self._uow.commit()
        return IngestionSourceCredentialSchema.model_validate(model)

    async def revoke(
        self, enterprise_id: UUID, source_id: UUID, credential_id: UUID
    ) -> IngestionSourceCredentialSchema:
        """Revoke an active ingestion-source credential.

        Args:
            enterprise_id: Expected owning enterprise identifier.
            source_id: Expected owning ingestion-source identifier.
            credential_id: Credential identifier to revoke.

        Returns:
            The revoked credential metadata response.

        Raises:
            InvalidIngestionSourceCredentialStateError: If already revoked or expired.
        """
        await self.get(enterprise_id, source_id, credential_id)
        current = await self._uow.ingestion_source_credentials.get_by_id_or_raise(
            credential_id
        )

        if current.status in (CredentialStatus.REVOKED, CredentialStatus.EXPIRED):
            raise InvalidIngestionSourceCredentialStateError(
                f'Credential with status "{current.status.value}" cannot be revoked.'
            )

        model = await self._uow.ingestion_source_credentials.update(
            credential_id,
            IngestionSourceCredentialUpdateSchema(status=CredentialStatus.REVOKED),
        )
        await self._uow.commit()
        return IngestionSourceCredentialSchema.model_validate(model)

    async def _get_source(
        self, enterprise_id: UUID, source_id: UUID
    ) -> IngestionSourceModel:
        """Return the active source after validating enterprise ownership.

        Args:
            enterprise_id: Expected owning enterprise identifier.
            source_id: Ingestion-source identifier to validate.

        Returns:
            The active ingestion-source model.

        Raises:
            IngestionSourceCredentialNotFoundError: If source ownership is invalid.
        """
        source = await self._uow.ingestion_sources.get_active_by_id_or_raise(source_id)
        if source.enterprise_id != enterprise_id:
            await self._uow.enterprises.get_active_by_id_or_raise(enterprise_id)
            raise IngestionSourceCredentialNotFoundError(
                f'Ingestion source "{source_id}" does not belong to enterprise.'
            )
        return source
