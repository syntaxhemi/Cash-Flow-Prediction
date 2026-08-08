from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from schemas.ingestion import (
    IngestionSourceCreateSchema,
    IngestionSourceCredentialCreateSchema,
    IngestionSourceCredentialFilterParams,
    IngestionSourceCredentialMetadataUpdateSchema,
    IngestionSourceCredentialSchema,
    IngestionSourceCredentialSecretUpdateSchema,
    IngestionSourceFilterParams,
    IngestionSourceSchema,
    IngestionSourceUpdateSchema,
)

from api.dependencies.services import (
    get_ingestion_source_credential_service,
    get_ingestion_source_service,
)
from api.schemas.ingestion_credentials import IngestionSourceCredentialListResponse
from api.schemas.ingestion_sources import IngestionSourceListResponse
from api.services.ingestion import (
    IngestionSourceCredentialService,
    IngestionSourceService,
)

router = APIRouter(
    prefix='/enterprises/{enterprise_id}/ingestion-sources',
    tags=['ingestion-sources'],
)


@router.post(
    '/{source_id}/credentials',
    response_model=IngestionSourceCredentialSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_ingestion_source_credential(
    enterprise_id: UUID,
    source_id: UUID,
    payload: IngestionSourceCredentialCreateSchema,
    service: Annotated[
        IngestionSourceCredentialService,
        Depends(get_ingestion_source_credential_service),
    ],
) -> IngestionSourceCredentialSchema:
    """Create a credential for an ingestion source."""
    return await service.create(enterprise_id, source_id, payload)


@router.get(
    '/{source_id}/credentials', response_model=IngestionSourceCredentialListResponse
)
async def list_ingestion_source_credentials(
    enterprise_id: UUID,
    source_id: UUID,
    filters: Annotated[IngestionSourceCredentialFilterParams, Depends()],
    service: Annotated[
        IngestionSourceCredentialService,
        Depends(get_ingestion_source_credential_service),
    ],
) -> IngestionSourceCredentialListResponse:
    """List credentials configured for an ingestion source."""
    return await service.list(enterprise_id, source_id, filters)


@router.get(
    '/{source_id}/credentials/{credential_id}',
    response_model=IngestionSourceCredentialSchema,
)
async def get_ingestion_source_credential(
    enterprise_id: UUID,
    source_id: UUID,
    credential_id: UUID,
    service: Annotated[
        IngestionSourceCredentialService,
        Depends(get_ingestion_source_credential_service),
    ],
) -> IngestionSourceCredentialSchema:
    """Return credential metadata for an ingestion source."""
    return await service.get(enterprise_id, source_id, credential_id)


@router.patch(
    '/{source_id}/credentials/{credential_id}',
    response_model=IngestionSourceCredentialSchema,
)
async def update_ingestion_source_credential(
    enterprise_id: UUID,
    source_id: UUID,
    credential_id: UUID,
    payload: IngestionSourceCredentialMetadataUpdateSchema,
    service: Annotated[
        IngestionSourceCredentialService,
        Depends(get_ingestion_source_credential_service),
    ],
) -> IngestionSourceCredentialSchema:
    """Update ingestion-source credential metadata."""
    return await service.update(enterprise_id, source_id, credential_id, payload)


@router.post(
    '/{source_id}/credentials/{credential_id}/rotate',
    response_model=IngestionSourceCredentialSchema,
)
async def rotate_ingestion_source_credential(
    enterprise_id: UUID,
    source_id: UUID,
    credential_id: UUID,
    payload: IngestionSourceCredentialSecretUpdateSchema,
    service: Annotated[
        IngestionSourceCredentialService,
        Depends(get_ingestion_source_credential_service),
    ],
) -> IngestionSourceCredentialSchema:
    """Replace an active ingestion-source credential value."""
    return await service.rotate(enterprise_id, source_id, credential_id, payload)


@router.post(
    '/{source_id}/credentials/{credential_id}/revoke',
    response_model=IngestionSourceCredentialSchema,
)
async def revoke_ingestion_source_credential(
    enterprise_id: UUID,
    source_id: UUID,
    credential_id: UUID,
    service: Annotated[
        IngestionSourceCredentialService,
        Depends(get_ingestion_source_credential_service),
    ],
) -> IngestionSourceCredentialSchema:
    """Revoke an ingestion-source credential."""
    return await service.revoke(enterprise_id, source_id, credential_id)


@router.post(
    '', response_model=IngestionSourceSchema, status_code=status.HTTP_201_CREATED
)
async def create_ingestion_source(
    enterprise_id: UUID,
    payload: IngestionSourceCreateSchema,
    service: Annotated[IngestionSourceService, Depends(get_ingestion_source_service)],
) -> IngestionSourceSchema:
    """Create an ingestion source for an enterprise."""
    return await service.create(enterprise_id, payload)


@router.get('', response_model=IngestionSourceListResponse)
async def list_ingestion_sources(
    enterprise_id: UUID,
    filters: Annotated[IngestionSourceFilterParams, Depends()],
    service: Annotated[IngestionSourceService, Depends(get_ingestion_source_service)],
) -> IngestionSourceListResponse:
    """List ingestion sources for an enterprise."""
    return await service.list(enterprise_id, filters)


@router.get('/{source_id}', response_model=IngestionSourceSchema)
async def get_ingestion_source(
    enterprise_id: UUID,
    source_id: UUID,
    service: Annotated[IngestionSourceService, Depends(get_ingestion_source_service)],
) -> IngestionSourceSchema:
    """Return an ingestion source belonging to an enterprise."""
    return await service.get(enterprise_id, source_id)


@router.patch('/{source_id}', response_model=IngestionSourceSchema)
async def update_ingestion_source(
    enterprise_id: UUID,
    source_id: UUID,
    payload: IngestionSourceUpdateSchema,
    service: Annotated[IngestionSourceService, Depends(get_ingestion_source_service)],
) -> IngestionSourceSchema:
    """Update an ingestion source belonging to an enterprise."""
    return await service.update(enterprise_id, source_id, payload)


@router.delete('/{source_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_ingestion_source(
    enterprise_id: UUID,
    source_id: UUID,
    service: Annotated[IngestionSourceService, Depends(get_ingestion_source_service)],
) -> None:
    """Soft-delete an ingestion source belonging to an enterprise."""
    await service.delete(enterprise_id, source_id)
