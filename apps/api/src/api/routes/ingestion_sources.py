from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from schemas.ingestion import (
    IngestionSourceCreateSchema,
    IngestionSourceFilterParams,
    IngestionSourceSchema,
    IngestionSourceUpdateSchema,
)

from api.dependencies.services import get_ingestion_source_service
from api.schemas.ingestion_sources import IngestionSourceListResponse
from api.services.ingestion import IngestionSourceService

router = APIRouter(
    prefix='/enterprises/{enterprise_id}/ingestion-sources',
    tags=['ingestion-sources'],
)


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
