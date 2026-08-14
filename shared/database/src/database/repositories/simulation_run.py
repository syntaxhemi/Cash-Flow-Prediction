from uuid import UUID

from domain.exceptions import (
    EnterpriseNotFoundError,
    InvalidForecastRunError,
    SimulationRunHasChildrenError,
    SimulationRunNotFoundError,
)
from schemas.simulation import (
    SimulationFilterParams,
    SimulationRunCreateSchema,
    SimulationRunUpdateSchema,
)
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import SimulationRunModel


class SimulationRunRepository:
    """Persist simulation-run records."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.

        Args:
            session: Async database session used for persistence operations.
        """
        self._session = session

    async def create(self, payload: SimulationRunCreateSchema) -> SimulationRunModel:
        """Create one simulation run.

        Args:
            payload: Validated simulation-run persistence data.

        Returns:
            The persisted simulation run.

        Raises:
        """
        run = SimulationRunModel(**payload.model_dump())
        self._session.add(run)

        try:
            await self._session.flush()

        except IntegrityError as error:
            if self._matches_constraint(
                error, 'fk_simulation_runs_enterprise_id_enterprises'
            ):
                raise EnterpriseNotFoundError(
                    f'Enterprise "{payload.enterprise_id}" does not exist.'
                ) from error

            if self._matches_constraint(
                error, 'fk_simulation_runs_forecast_run_id_forecast_runs'
            ):
                raise InvalidForecastRunError(
                    f'Forecast run "{payload.forecast_run_id}" does not exist.'
                ) from error
            raise

        await self._session.refresh(run)
        return run

    async def get_by_id(self, run_id: UUID) -> SimulationRunModel | None:
        """Return a simulation run by identifier when it exists.

        Args:
            run_id: Simulation-run identifier.

        Returns:
            The matching simulation run, or ``None``.
        """
        result = await self._session.execute(
            select(SimulationRunModel).where(SimulationRunModel.id == run_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_outputs(self, run_id: UUID) -> SimulationRunModel | None:
        """Return a simulation run with all persisted outputs loaded.

        Args:
            run_id: Simulation-run identifier.

        Returns:
            The matching simulation run with scenarios, rankings, and
            recommendations loaded, or ``None``.
        """
        result = await self._session.execute(
            select(SimulationRunModel)
            .where(SimulationRunModel.id == run_id)
            .options(
                selectinload(SimulationRunModel.scenarios),
                selectinload(SimulationRunModel.receivables_rankings),
                selectinload(SimulationRunModel.mitigation_recommendations),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(self, run_id: UUID) -> SimulationRunModel:
        """Return a simulation run or raise when it is missing.

        Args:
            run_id: Simulation-run identifier.

        Returns:
            The matching simulation run.

        Raises:
            SimulationRunNotFoundError: If no simulation run exists.
        """
        run = await self.get_by_id(run_id)
        if run is None:
            raise SimulationRunNotFoundError(
                f'Simulation run "{run_id}" does not exist.'
            )
        return run

    async def list_for_enterprise(
        self, enterprise_id: UUID
    ) -> list[SimulationRunModel]:
        """List simulation runs for an enterprise, newest first.

        Args:
            enterprise_id: Owning enterprise identifier.

        Returns:
            Matching simulation runs ordered by creation time descending.
        """
        result = await self._session.execute(
            select(SimulationRunModel)
            .where(SimulationRunModel.enterprise_id == enterprise_id)
            .order_by(SimulationRunModel.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_for_enterprise_with_outputs(
        self, enterprise_id: UUID, filters: SimulationFilterParams
    ) -> list[SimulationRunModel]:
        """List simulation runs with persisted outputs for an enterprise.

        Args:
            enterprise_id: Owning enterprise identifier.

        Returns:
            Matching simulation runs with child outputs loaded newest first.
        """
        statement = select(SimulationRunModel).where(
            SimulationRunModel.enterprise_id == enterprise_id
        )
        if filters.simulation_type is not None:
            statement = statement.where(
                SimulationRunModel.simulation_type == filters.simulation_type
            )
        if filters.status is not None:
            statement = statement.where(SimulationRunModel.status == filters.status)
        if filters.created_from is not None:
            statement = statement.where(
                SimulationRunModel.created_at >= filters.created_from
            )
        if filters.created_to is not None:
            statement = statement.where(
                SimulationRunModel.created_at <= filters.created_to
            )
        result = await self._session.execute(
            statement.options(
                selectinload(SimulationRunModel.scenarios),
                selectinload(SimulationRunModel.receivables_rankings),
                selectinload(SimulationRunModel.mitigation_recommendations),
            )
            .order_by(SimulationRunModel.created_at.desc())
            .limit(filters.limit)
            .offset(filters.offset)
        )
        return list(result.scalars().all())

    async def update(
        self, run_id: UUID, payload: SimulationRunUpdateSchema
    ) -> SimulationRunModel:
        """Update mutable simulation-run fields.

        Args:
            run_id: Simulation-run identifier.
            payload: Validated fields to update.

        Returns:
            The updated simulation run.

        Raises:
            SimulationRunNotFoundError: If no simulation run exists.
        """
        run = await self.get_by_id_or_raise(run_id)

        for name, value in payload.model_dump(exclude_unset=True).items():
            setattr(run, name, value)

        await self._session.flush()
        await self._session.refresh(run)
        return run

    async def delete(self, run_id: UUID) -> None:
        """Delete one simulation run.

        Args:
            run_id: Simulation-run identifier.

        Raises:
            SimulationRunNotFoundError: If no simulation run exists.
            SimulationRunHasChildrenError: If persisted outputs reference the run.
        """
        await self.get_by_id_or_raise(run_id)

        try:
            await self._session.execute(
                delete(SimulationRunModel).where(SimulationRunModel.id == run_id)
            )
            await self._session.flush()

        except IntegrityError as error:
            if self._matches_constraint(
                error,
                'fk_simulation_scenarios_simulation_run_id_simulation_runs',
                'fk_receivables_rankings_simulation_run_id_simulation_runs',
                'fk_mitigation_recommendations_simulation_run_id_simulation_runs',
            ):
                raise SimulationRunHasChildrenError(
                    f'Simulation run "{run_id}" cannot be deleted while outputs exist.'
                ) from error
            raise

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
