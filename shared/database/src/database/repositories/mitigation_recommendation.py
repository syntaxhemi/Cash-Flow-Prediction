from uuid import UUID

from domain.exceptions import (
    InvalidSimulationError,
    MitigationRecommendationNotFoundError,
    SimulationRunNotFoundError,
)
from schemas.simulation import (
    MitigationRecommendationCreateSchema,
    MitigationRecommendationUpdateSchema,
)
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import MitigationRecommendationModel


class MitigationRecommendationRepository:
    """Persist liquidity mitigation recommendation records."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.

        Args:
            session: Async database session used for persistence operations.
        """
        self._session = session

    async def create(
        self,
        simulation_run_id: UUID,
        payload: MitigationRecommendationCreateSchema,
    ) -> MitigationRecommendationModel:
        """Create one mitigation recommendation.

        Args:
            simulation_run_id: Parent simulation-run identifier.
            payload: Validated recommendation persistence data.

        Returns:
            The persisted recommendation.

        Raises:
            SimulationRunNotFoundError: If the parent simulation does not exist.
            InvalidSimulationError: If the priority rank is duplicated.
        """
        row = MitigationRecommendationModel(
            simulation_run_id=simulation_run_id, **payload.model_dump()
        )
        self._session.add(row)

        try:
            await self._session.flush()

        except IntegrityError as error:
            if self._matches_constraint(
                error, 'fk_mitigation_recommendations_simulation_run_id_simulation_runs'
            ):
                raise SimulationRunNotFoundError(
                    f'Simulation run "{simulation_run_id}" does not exist.'
                ) from error

            if self._matches_constraint(
                error,
                'uq_mitigation_recommendations_simulation_run_id',
                'mitigation_recommendations_simulation_run_id_priority_rank_key',
            ):
                raise InvalidSimulationError(
                    'A recommendation with this priority already exists for the '
                    'simulation.'
                ) from error
            raise

        await self._session.refresh(row)
        return row

    async def create_many(
        self,
        simulation_run_id: UUID,
        payloads: list[MitigationRecommendationCreateSchema],
    ) -> list[MitigationRecommendationModel]:
        """Create multiple recommendations for one simulation run.

        Args:
            simulation_run_id: Parent simulation-run identifier.
            payloads: Validated recommendation persistence data.

        Returns:
            The persisted recommendations in input order.

        Raises:
            SimulationRunNotFoundError: If the parent simulation does not exist.
            InvalidSimulationError: If a priority rank is duplicated.
        """
        rows = [
            MitigationRecommendationModel(
                simulation_run_id=simulation_run_id, **payload.model_dump()
            )
            for payload in payloads
        ]
        self._session.add_all(rows)

        try:
            await self._session.flush()

        except IntegrityError as error:
            if self._matches_constraint(
                error, 'fk_mitigation_recommendations_simulation_run_id_simulation_runs'
            ):
                raise SimulationRunNotFoundError(
                    f'Simulation run "{simulation_run_id}" does not exist.'
                ) from error

            if self._matches_constraint(
                error,
                'uq_mitigation_recommendations_simulation_run_id',
                'mitigation_recommendations_simulation_run_id_priority_rank_key',
            ):
                raise InvalidSimulationError(
                    'A recommendation with this priority already exists for the '
                    'simulation.'
                ) from error
            raise

        for row in rows:
            await self._session.refresh(row)

        return rows

    async def get_by_id(
        self, recommendation_id: UUID
    ) -> MitigationRecommendationModel | None:
        """Return a recommendation by identifier when it exists.

        Args:
            recommendation_id: Recommendation identifier.

        Returns:
            The matching recommendation, or ``None``.
        """
        result = await self._session.execute(
            select(MitigationRecommendationModel).where(
                MitigationRecommendationModel.id == recommendation_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(
        self, recommendation_id: UUID
    ) -> MitigationRecommendationModel:
        """Return a recommendation or raise when it is missing.

        Args:
            recommendation_id: Recommendation identifier.

        Returns:
            The matching recommendation.

        Raises:
            MitigationRecommendationNotFoundError: If no recommendation exists.
        """
        row = await self.get_by_id(recommendation_id)
        if row is None:
            raise MitigationRecommendationNotFoundError(
                f'Mitigation recommendation "{recommendation_id}" does not exist.'
            )
        return row

    async def list_for_run(
        self, simulation_run_id: UUID
    ) -> list[MitigationRecommendationModel]:
        """List recommendations for a simulation run by priority.

        Args:
            simulation_run_id: Parent simulation-run identifier.

        Returns:
            Persisted recommendations ordered by priority rank.
        """
        result = await self._session.execute(
            select(MitigationRecommendationModel)
            .where(MitigationRecommendationModel.simulation_run_id == simulation_run_id)
            .order_by(MitigationRecommendationModel.priority_rank)
        )
        return list(result.scalars().all())

    async def update(
        self,
        recommendation_id: UUID,
        payload: MitigationRecommendationUpdateSchema,
    ) -> MitigationRecommendationModel:
        """Update mutable recommendation fields.

        Args:
            recommendation_id: Recommendation identifier.
            payload: Validated fields to update.

        Returns:
            The updated recommendation.

        Raises:
            MitigationRecommendationNotFoundError: If no recommendation exists.
            InvalidSimulationError: If the priority rank is duplicated.
        """
        row = await self.get_by_id_or_raise(recommendation_id)

        for name, value in payload.model_dump(exclude_unset=True).items():
            setattr(row, name, value)

        try:
            await self._session.flush()

        except IntegrityError as error:
            if self._matches_constraint(
                error,
                'uq_mitigation_recommendations_simulation_run_id',
                'mitigation_recommendations_simulation_run_id_priority_rank_key',
            ):
                raise InvalidSimulationError(
                    'A recommendation with this priority already exists for the '
                    'simulation.'
                ) from error
            raise

        await self._session.refresh(row)
        return row

    async def delete(self, recommendation_id: UUID) -> None:
        """Delete one mitigation recommendation.

        Args:
            recommendation_id: Recommendation identifier.

        Raises:
            MitigationRecommendationNotFoundError: If no recommendation exists.
        """
        await self.get_by_id_or_raise(recommendation_id)

        await self._session.execute(
            delete(MitigationRecommendationModel).where(
                MitigationRecommendationModel.id == recommendation_id
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
