from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from schemas.forecasting import ForecastRequestSchema, ForecastRunSchema
from schemas.simulation import (
    HealthDeltaRequestSchema,
    SimulationRunSchema,
    TrappedLiquidityRequestSchema,
)

from api.dependencies.services import (
    get_baseline_forecast_service,
    get_health_delta_simulation_service,
    get_trapped_liquidity_simulation_service,
)
from api.services.forecasting import (
    BaselineForecastService,
    HealthDeltaSimulationService,
    TrappedLiquiditySimulationService,
)

router = APIRouter(prefix='/enterprises/{enterprise_id}/forecasts', tags=['forecasts'])


@router.post('', response_model=ForecastRunSchema, status_code=status.HTTP_201_CREATED)
async def create_baseline_forecast(
    enterprise_id: UUID,
    payload: ForecastRequestSchema,
    service: Annotated[BaselineForecastService, Depends(get_baseline_forecast_service)],
) -> ForecastRunSchema:
    """Run and persist a baseline forecast for an enterprise."""
    return await service.create(enterprise_id, payload)


@router.post(
    '/{forecast_run_id}/simulations/health-delta',
    response_model=SimulationRunSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_health_delta_simulation(
    enterprise_id: UUID,
    forecast_run_id: UUID,
    payload: HealthDeltaRequestSchema,
    service: Annotated[
        HealthDeltaSimulationService, Depends(get_health_delta_simulation_service)
    ],
) -> SimulationRunSchema:
    """Run and persist health delta scenarios for a baseline forecast."""
    return await service.create(enterprise_id, forecast_run_id, payload)


@router.post(
    '/{forecast_run_id}/simulations/trapped-liquidity',
    response_model=SimulationRunSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_trapped_liquidity_simulation(
    enterprise_id: UUID,
    forecast_run_id: UUID,
    payload: TrappedLiquidityRequestSchema,
    service: Annotated[
        TrappedLiquiditySimulationService,
        Depends(get_trapped_liquidity_simulation_service),
    ],
) -> SimulationRunSchema:
    """Run trapped-liquidity analysis for a baseline forecast."""
    return await service.create(enterprise_id, forecast_run_id, payload)
