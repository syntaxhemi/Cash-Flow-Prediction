from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from schemas.financial import (
    StaticFinancialSnapshotCreateSchema,
    StaticFinancialSnapshotSchema,
    StaticFinancialSnapshotUpdateSchema,
)

from api.dependencies.services import get_static_financial_snapshot_service
from api.services.financial import StaticFinancialSnapshotService

router = APIRouter(prefix='/enterprises/{enterprise_id}/financial', tags=['financial'])


@router.post(
    '/static-snapshots',
    response_model=StaticFinancialSnapshotSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_static_snapshot(
    enterprise_id: UUID,
    payload: StaticFinancialSnapshotCreateSchema,
    service: Annotated[
        StaticFinancialSnapshotService, Depends(get_static_financial_snapshot_service)
    ],
) -> StaticFinancialSnapshotSchema:
    """Create a static financial snapshot."""
    return await service.create(enterprise_id, payload)


@router.get('/static-snapshots', response_model=list[StaticFinancialSnapshotSchema])
async def list_static_snapshots(
    enterprise_id: UUID,
    service: Annotated[
        StaticFinancialSnapshotService, Depends(get_static_financial_snapshot_service)
    ],
) -> list[StaticFinancialSnapshotSchema]:
    """List static financial snapshots for an enterprise."""
    return await service.list(enterprise_id)


@router.get('/static-snapshots/latest', response_model=StaticFinancialSnapshotSchema)
async def get_latest_static_snapshot(
    enterprise_id: UUID,
    target_date: Annotated[date, Query()],
    service: Annotated[
        StaticFinancialSnapshotService, Depends(get_static_financial_snapshot_service)
    ],
) -> StaticFinancialSnapshotSchema:
    """Return the latest applicable static financial snapshot."""
    return await service.latest(enterprise_id, target_date)


@router.get(
    '/static-snapshots/{snapshot_id}', response_model=StaticFinancialSnapshotSchema
)
async def get_static_snapshot(
    enterprise_id: UUID,
    snapshot_id: UUID,
    service: Annotated[
        StaticFinancialSnapshotService, Depends(get_static_financial_snapshot_service)
    ],
) -> StaticFinancialSnapshotSchema:
    """Return one static financial snapshot."""
    return await service.get(enterprise_id, snapshot_id)


@router.patch(
    '/static-snapshots/{snapshot_id}', response_model=StaticFinancialSnapshotSchema
)
async def update_static_snapshot(
    enterprise_id: UUID,
    snapshot_id: UUID,
    payload: StaticFinancialSnapshotUpdateSchema,
    service: Annotated[
        StaticFinancialSnapshotService, Depends(get_static_financial_snapshot_service)
    ],
) -> StaticFinancialSnapshotSchema:
    """Update one static financial snapshot."""
    return await service.update(enterprise_id, snapshot_id, payload)
