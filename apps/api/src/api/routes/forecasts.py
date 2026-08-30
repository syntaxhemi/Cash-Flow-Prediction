from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from schemas.forecasting import (
    ForecastFilterParams,
    ForecastRequestSchema,
    ForecastRunSchema,
)
from schemas.simulation import (
    HealthDeltaRequestSchema,
    LiquidityMitigationRequestSchema,
    SimulationRunSchema,
    TrappedLiquidityRequestSchema,
)

from api.dependencies.services import (
    get_baseline_forecast_service,
    get_health_delta_simulation_service,
    get_liquidity_mitigation_service,
    get_trapped_liquidity_simulation_service,
)
from api.schemas.forecasts import ForecastListResponse
from api.services.forecasting import (
    BaselineForecastService,
    HealthDeltaSimulationService,
    LiquidityMitigationService,
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


@router.get('', response_model=ForecastListResponse)
async def list_forecasts(
    enterprise_id: UUID,
    filters: Annotated[ForecastFilterParams, Depends()],
    service: Annotated[BaselineForecastService, Depends(get_baseline_forecast_service)],
) -> ForecastListResponse:
    """List forecast history and the recorded periods used by each run.

    Args:
        enterprise_id: Owning enterprise identifier.
        filters: Run filters and pagination parameters.
        service: Baseline forecast application service.

    Returns:
        Paginated forecast history.
    """
    return await service.list_forecasts(enterprise_id, filters)


@router.get('/{forecast_run_id}', response_model=ForecastRunSchema)
async def get_forecast(
    enterprise_id: UUID,
    forecast_run_id: UUID,
    service: Annotated[BaselineForecastService, Depends(get_baseline_forecast_service)],
) -> ForecastRunSchema:
    """Return one forecast with its model inputs and derived observations."""
    return await service.get(enterprise_id, forecast_run_id)


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


@router.post(
    '/{forecast_run_id}/simulations/liquidity-mitigation',
    response_model=SimulationRunSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_liquidity_mitigation_simulation(
    enterprise_id: UUID,
    forecast_run_id: UUID,
    payload: LiquidityMitigationRequestSchema,
    service: Annotated[
        LiquidityMitigationService, Depends(get_liquidity_mitigation_service)
    ],
) -> SimulationRunSchema:
    """Generate bounded liquidity mitigation recommendations."""
    return await service.create(enterprise_id, forecast_run_id, payload)
