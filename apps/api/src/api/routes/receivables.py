from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from schemas.financial import ReceivablesFilterParams, ReceivablesListResponse

from api.dependencies.services import get_receivables_service
from api.services.receivables import ReceivablesService

router = APIRouter(
    prefix='/enterprises/{enterprise_id}/receivables', tags=['receivables']
)


@router.get('', response_model=ReceivablesListResponse)
async def list_receivables(
    enterprise_id: UUID,
    filters: Annotated[ReceivablesFilterParams, Depends()],
    service: Annotated[ReceivablesService, Depends(get_receivables_service)],
) -> ReceivablesListResponse:
    """Return receivable details and supporting records for a forecast."""
    return await service.get_for_forecast(enterprise_id, filters)
