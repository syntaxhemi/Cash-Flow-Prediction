from uuid import UUID

from domain.exceptions import (
    InvalidSimulationError,
    SimulationRunNotFoundError,
    SimulationScenarioNotFoundError,
)
from schemas.simulation import (
    SimulationScenarioCreateSchema,
    SimulationScenarioUpdateSchema,
)
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import SimulationScenarioModel


class SimulationScenarioRepository:
    """Persist simulation scenario records."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.

        Args:
            session: Async database session used for persistence operations.
        """
        self._session = session

    async def create(
        self, simulation_run_id: UUID, payload: SimulationScenarioCreateSchema
    ) -> SimulationScenarioModel:
        """Create one simulation scenario.

        Args:
            simulation_run_id: Parent simulation-run identifier.
            payload: Validated scenario persistence data.

        Returns:
            The persisted scenario.

        Raises:
            InvalidSimulationError: If a database constraint is violated.
        """
        row = SimulationScenarioModel(
            simulation_run_id=simulation_run_id, **payload.model_dump()
        )
        self._session.add(row)

        try:
            await self._session.flush()

        except IntegrityError as error:
            if self._matches_constraint(
                error, 'fk_simulation_scenarios_simulation_run_id_simulation_runs'
            ):
                raise SimulationRunNotFoundError(
                    f'Simulation run "{simulation_run_id}" does not exist.'
                ) from error

            if self._matches_constraint(
                error,
                'uq_simulation_scenarios_simulation_run_id',
                'simulation_scenarios_simulation_run_id_scenario_index_key',
            ):
                raise InvalidSimulationError(
                    'A scenario with this index already exists for the simulation.'
                ) from error
            raise

        await self._session.refresh(row)
        return row

    async def create_many(
        self, simulation_run_id: UUID, payloads: list[SimulationScenarioCreateSchema]
    ) -> list[SimulationScenarioModel]:
        """Create multiple scenarios for one simulation run.

        Args:
            simulation_run_id: Parent simulation-run identifier.
            payloads: Validated scenario persistence data.

        Returns:
            The persisted scenarios in input order.

        Raises:
            InvalidSimulationError: If a database constraint is violated.
        """
        rows = [
            SimulationScenarioModel(
                simulation_run_id=simulation_run_id, **payload.model_dump()
            )
            for payload in payloads
        ]
        self._session.add_all(rows)

        try:
            await self._session.flush()

        except IntegrityError as error:
            if self._matches_constraint(
                error, 'fk_simulation_scenarios_simulation_run_id_simulation_runs'
            ):
                raise SimulationRunNotFoundError(
                    f'Simulation run "{simulation_run_id}" does not exist.'
                ) from error

            if self._matches_constraint(
                error,
                'uq_simulation_scenarios_simulation_run_id',
                'simulation_scenarios_simulation_run_id_scenario_index_key',
            ):
                raise InvalidSimulationError(
                    'A scenario with this index already exists for the simulation.'
                ) from error
            raise

        for row in rows:
            await self._session.refresh(row)

        return rows

    async def get_by_id(self, scenario_id: UUID) -> SimulationScenarioModel | None:
        """Return a scenario by identifier when it exists.

        Args:
            scenario_id: Scenario identifier.

        Returns:
            The matching scenario, or ``None``.
        """
        result = await self._session.execute(
            select(SimulationScenarioModel).where(
                SimulationScenarioModel.id == scenario_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(self, scenario_id: UUID) -> SimulationScenarioModel:
        """Return a scenario or raise when it is missing.

        Args:
            scenario_id: Scenario identifier.

        Returns:
            The matching scenario.

        Raises:
            SimulationScenarioNotFoundError: If no scenario exists.
        """
        row = await self.get_by_id(scenario_id)
        if row is None:
            raise SimulationScenarioNotFoundError(
                f'Simulation scenario "{scenario_id}" does not exist.'
            )
        return row

    async def list_for_run(
        self, simulation_run_id: UUID
    ) -> list[SimulationScenarioModel]:
        """List scenarios for a simulation run in scenario order.

        Args:
            simulation_run_id: Parent simulation-run identifier.

        Returns:
            Persisted scenarios ordered by scenario index.
        """
        result = await self._session.execute(
            select(SimulationScenarioModel)
            .where(SimulationScenarioModel.simulation_run_id == simulation_run_id)
            .order_by(SimulationScenarioModel.scenario_index)
        )
        return list(result.scalars().all())

    async def update(
        self, scenario_id: UUID, payload: SimulationScenarioUpdateSchema
    ) -> SimulationScenarioModel:
        """Update mutable scenario fields.

        Args:
            scenario_id: Scenario identifier.
            payload: Validated fields to update.

        Returns:
            The updated scenario.

        Raises:
            SimulationScenarioNotFoundError: If no scenario exists.
            InvalidSimulationError: If a database constraint is violated.
        """
        row = await self.get_by_id_or_raise(scenario_id)

        for name, value in payload.model_dump(exclude_unset=True).items():
            setattr(row, name, value)

        try:
            await self._session.flush()

        except IntegrityError as error:
            if self._matches_constraint(
                error,
                'uq_simulation_scenarios_simulation_run_id',
                'simulation_scenarios_simulation_run_id_scenario_index_key',
            ):
                raise InvalidSimulationError(
                    'A scenario with this index already exists for the simulation.'
                ) from error
            raise

        await self._session.refresh(row)
        return row

    async def delete(self, scenario_id: UUID) -> None:
        """Delete one simulation scenario.

        Args:
            scenario_id: Scenario identifier.

        Raises:
            SimulationScenarioNotFoundError: If no scenario exists.
        """
        await self.get_by_id_or_raise(scenario_id)

        await self._session.execute(
            delete(SimulationScenarioModel).where(
                SimulationScenarioModel.id == scenario_id
            )
        )
        await self._session.flush()

    @staticmethod
    def _matches_constraint(error: IntegrityError, *constraint_names: str) -> bool:
        """Return whether an integrity error references a known constraint.

        Args:
            error: Integrity error raised by the database.
            *constraint_names: Constraint names to match.

        Returns:
            ``True`` when the error references one of the supplied constraints.
        """
        return any(name in str(error.orig) for name in constraint_names)
