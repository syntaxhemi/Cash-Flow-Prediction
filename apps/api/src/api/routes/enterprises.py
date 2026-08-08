from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from schemas.enterprise import (
    EnterpriseCreateSchema,
    EnterpriseFilterParams,
    EnterpriseSchema,
    EnterpriseUpdateSchema,
)

from api.dependencies.services import get_enterprise_service
from api.schemas.enterprise import EnterpriseListResponse
from api.services.enterprise import EnterpriseService

router = APIRouter(prefix='/enterprises', tags=['enterprises'])


@router.post('', response_model=EnterpriseSchema, status_code=status.HTTP_201_CREATED)
async def create_enterprise(
    payload: EnterpriseCreateSchema,
    service: Annotated[EnterpriseService, Depends(get_enterprise_service)],
) -> EnterpriseSchema:
    """Create an enterprise.

    Args:
        payload: Enterprise creation payload.
        service: Enterprise application service.

    Returns:
        Created enterprise response.
    """
    return await service.create(payload)


@router.get('', response_model=EnterpriseListResponse)
async def list_enterprises(
    filters: Annotated[EnterpriseFilterParams, Depends()],
    service: Annotated[EnterpriseService, Depends(get_enterprise_service)],
) -> EnterpriseListResponse:
    """List enterprises matching query filters."""
    return await service.list(filters)


@router.get('/{enterprise_id}', response_model=EnterpriseSchema)
async def get_enterprise(
    enterprise_id: UUID,
    service: Annotated[EnterpriseService, Depends(get_enterprise_service)],
) -> EnterpriseSchema:
    """Return an enterprise by identifier."""
    return await service.get(enterprise_id)


@router.patch('/{enterprise_id}', response_model=EnterpriseSchema)
async def update_enterprise(
    enterprise_id: UUID,
    payload: EnterpriseUpdateSchema,
    service: Annotated[EnterpriseService, Depends(get_enterprise_service)],
) -> EnterpriseSchema:
    """Update an enterprise by identifier."""
    return await service.update(enterprise_id, payload)


@router.delete('/{enterprise_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_enterprise(
    enterprise_id: UUID,
    service: Annotated[EnterpriseService, Depends(get_enterprise_service)],
) -> Response:
    """Soft-delete an enterprise by deactivating it.

    Args:
        enterprise_id: Enterprise identifier to deactivate.
        service: Enterprise application service.

    Returns:
        Empty no-content response.
    """
    await service.delete(enterprise_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
