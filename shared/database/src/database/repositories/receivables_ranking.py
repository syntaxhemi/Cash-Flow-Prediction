from uuid import UUID

from domain.exceptions import (
    CounterpartyNotFoundError,
    InvalidSimulationError,
    ReceivablesRankingNotFoundError,
    SimulationRunNotFoundError,
)
from schemas.simulation import (
    ReceivablesRankingCreateSchema,
    ReceivablesRankingUpdateSchema,
)
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import ReceivablesRankingModel


class ReceivablesRankingRepository:
    """Persist trapped-liquidity ranking records."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.

        Args:
            session: Async database session used for persistence operations.
        """
        self._session = session

    async def create(
        self, simulation_run_id: UUID, payload: ReceivablesRankingCreateSchema
    ) -> ReceivablesRankingModel:
        """Create one receivables ranking.

        Args:
            simulation_run_id: Parent simulation-run identifier.
            payload: Validated ranking persistence data.

        Returns:
            The persisted ranking.

        Raises:
            InvalidSimulationError: If a database constraint is violated.
        """
        row = ReceivablesRankingModel(
            simulation_run_id=simulation_run_id, **payload.model_dump()
        )
        self._session.add(row)

        try:
            await self._session.flush()

        except IntegrityError as error:
            if self._matches_constraint(
                error, 'fk_receivables_rankings_simulation_run_id_simulation_runs'
            ):
                raise SimulationRunNotFoundError(
                    f'Simulation run "{simulation_run_id}" does not exist.'
                ) from error

            if self._matches_constraint(
                error, 'fk_receivables_rankings_counterparty_id_counterparties'
            ):
                raise CounterpartyNotFoundError(
                    f'Counterparty "{payload.counterparty_id}" does not exist.'
                ) from error

            if self._matches_constraint(
                error,
                'uq_receivables_rankings_simulation_run_id',
                'receivables_rankings_simulation_run_id_counterparty_id_key',
            ):
                raise InvalidSimulationError(
                    'A ranking already exists for this simulation and counterparty.'
                ) from error
            raise

        await self._session.refresh(row)
        return row

    async def get_by_id(self, ranking_id: UUID) -> ReceivablesRankingModel | None:
        """Return a ranking by identifier when it exists.

        Args:
            ranking_id: Ranking identifier.

        Returns:
            The matching ranking, or ``None``.
        """
        result = await self._session.execute(
            select(ReceivablesRankingModel).where(
                ReceivablesRankingModel.id == ranking_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(self, ranking_id: UUID) -> ReceivablesRankingModel:
        """Return a ranking or raise when it is missing.

        Args:
            ranking_id: Ranking identifier.

        Returns:
            The matching ranking.

        Raises:
            ReceivablesRankingNotFoundError: If no ranking exists.
        """
        row = await self.get_by_id(ranking_id)
        if row is None:
            raise ReceivablesRankingNotFoundError(
                f'Receivables ranking "{ranking_id}" does not exist.'
            )
        return row

    async def list_for_run(
        self, simulation_run_id: UUID
    ) -> list[ReceivablesRankingModel]:
        """List rankings for a simulation run by rank position.

        Args:
            simulation_run_id: Parent simulation-run identifier.

        Returns:
            Persisted rankings ordered by rank position.
        """
        result = await self._session.execute(
            select(ReceivablesRankingModel)
            .where(ReceivablesRankingModel.simulation_run_id == simulation_run_id)
            .order_by(ReceivablesRankingModel.rank_position)
        )
        return list(result.scalars().all())

    async def update(
        self, ranking_id: UUID, payload: ReceivablesRankingUpdateSchema
    ) -> ReceivablesRankingModel:
        """Update mutable ranking fields.

        Args:
            ranking_id: Ranking identifier.
            payload: Validated fields to update.

        Returns:
            The updated ranking.

        Raises:
            ReceivablesRankingNotFoundError: If no ranking exists.
            InvalidSimulationError: If a database constraint is violated.
        """
        row = await self.get_by_id_or_raise(ranking_id)

        for name, value in payload.model_dump(exclude_unset=True).items():
            setattr(row, name, value)

        try:
            await self._session.flush()

        except IntegrityError as error:
            if self._matches_constraint(
                error, 'uq_receivables_rankings_simulation_run_id'
            ):
                raise InvalidSimulationError(
                    'A ranking already exists for this simulation and counterparty.'
                ) from error
            raise

        await self._session.refresh(row)
        return row

    async def delete(self, ranking_id: UUID) -> None:
        """Delete one receivables ranking.

        Args:
            ranking_id: Ranking identifier.

        Raises:
            ReceivablesRankingNotFoundError: If no ranking exists.
        """
        await self.get_by_id_or_raise(ranking_id)

        await self._session.execute(
            delete(ReceivablesRankingModel).where(
                ReceivablesRankingModel.id == ranking_id
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
