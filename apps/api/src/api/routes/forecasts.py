from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from schemas.forecasting import ForecastRequestSchema, ForecastRunSchema

from api.dependencies.services import get_baseline_forecast_service
from api.services.forecasting import BaselineForecastService

router = APIRouter(prefix='/enterprises/{enterprise_id}/forecasts', tags=['forecasts'])


@router.post('', response_model=ForecastRunSchema, status_code=status.HTTP_201_CREATED)
async def create_baseline_forecast(
    enterprise_id: UUID,
    payload: ForecastRequestSchema,
    service: Annotated[BaselineForecastService, Depends(get_baseline_forecast_service)],
) -> ForecastRunSchema:
    """Run and persist a baseline forecast for an enterprise."""
    return await service.create(enterprise_id, payload)
