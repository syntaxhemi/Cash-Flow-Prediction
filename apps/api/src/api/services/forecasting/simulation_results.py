from uuid import UUID

from database import IUnitOfWork
from database.models import SimulationRunModel
from domain.exceptions import InvalidSimulationError
from schemas.simulation import (
    MitigationRecommendationSchema,
    ReceivablesRankingSchema,
    SimulationFilterParams,
    SimulationRunSchema,
    SimulationScenarioSchema,
)


class SimulationResultService:
    """Retrieve persisted simulation runs and their outputs."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize the simulation result service.

        Args:
            uow: Request-scoped unit of work used for result queries.
        """
        self._uow = uow

    async def list(
        self, enterprise_id: UUID, filters: SimulationFilterParams
    ) -> list[SimulationRunSchema]:
        """List persisted simulation results for an enterprise.

        Args:
            enterprise_id: Owning enterprise identifier.
            filters: Simulation type and lifecycle status filters.

        Returns:
            Simulation runs with all persisted output collections.
        """
        await self._uow.enterprises.get_active_by_id_or_raise(enterprise_id)
        runs = await self._uow.simulation_runs.list_for_enterprise_with_outputs(
            enterprise_id, filters
        )
        return [self._to_schema(run) for run in runs]

    async def get(
        self, enterprise_id: UUID, simulation_run_id: UUID
    ) -> SimulationRunSchema:
        """Retrieve one persisted simulation result.

        Args:
            enterprise_id: Owning enterprise identifier.
            simulation_run_id: Simulation-run identifier.

        Returns:
            The matching simulation run with all persisted outputs.

        Raises:
            InvalidSimulationError: If the run does not belong to the enterprise.
        """
        await self._uow.enterprises.get_active_by_id_or_raise(enterprise_id)
        run = await self._uow.simulation_runs.get_by_id_with_outputs(simulation_run_id)
        if run is None or run.enterprise_id != enterprise_id:
            raise InvalidSimulationError(
                f'Simulation run "{simulation_run_id}" does not belong to the '
                'enterprise.'
            )
        return self._to_schema(run)

    @staticmethod
    def _to_schema(run: SimulationRunModel) -> SimulationRunSchema:
        """Convert a loaded simulation ORM model to its response schema.

        Args:
            run: Loaded simulation ORM model with output relationships.

        Returns:
            API response schema containing all output collections.
        """
        return SimulationRunSchema(
            id=run.id,
            enterprise_id=run.enterprise_id,
            forecast_run_id=run.forecast_run_id,
            simulation_type=run.simulation_type,
            status=run.status,
            summary_result=run.summary_result,
            requested_at=run.requested_at,
            completed_at=run.completed_at,
            created_at=run.created_at,
            scenarios=[
                SimulationScenarioSchema.model_validate(row) for row in run.scenarios
            ],
            receivables_rankings=[
                ReceivablesRankingSchema.model_validate(row)
                for row in run.receivables_rankings
            ],
            mitigation_recommendations=[
                MitigationRecommendationSchema.model_validate(row)
                for row in run.mitigation_recommendations
            ],
        )
