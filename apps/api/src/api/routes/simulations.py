from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from schemas.simulation import SimulationFilterParams, SimulationRunSchema

from api.dependencies.services import get_simulation_result_service
from api.services.forecasting import SimulationResultService

router = APIRouter(
    prefix='/enterprises/{enterprise_id}/simulations', tags=['simulations']
)


@router.get('', response_model=list[SimulationRunSchema])
async def list_simulation_results(
    enterprise_id: UUID,
    filters: Annotated[SimulationFilterParams, Depends()],
    service: Annotated[SimulationResultService, Depends(get_simulation_result_service)],
) -> list[SimulationRunSchema]:
    """List persisted simulation results for an enterprise."""
    return await service.list(enterprise_id, filters)


@router.get('/{simulation_run_id}', response_model=SimulationRunSchema)
async def get_simulation_result(
    enterprise_id: UUID,
    simulation_run_id: UUID,
    service: Annotated[SimulationResultService, Depends(get_simulation_result_service)],
) -> SimulationRunSchema:
    """Return one persisted simulation result for an enterprise."""
    return await service.get(enterprise_id, simulation_run_id)
