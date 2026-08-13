from datetime import date
from uuid import UUID

from domain.exceptions import (
    StaticFinancialSnapshotAlreadyExistsError,
    StaticFinancialSnapshotNotFoundError,
)
from schemas.financial import (
    StaticFinancialSnapshotCreateSchema,
    StaticFinancialSnapshotUpdateSchema,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import StaticFinancialSnapshotModel


class StaticFinancialSnapshotRepository:
    """Persist and retrieve enterprise-scoped static feature snapshots."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.

        Args:
            session: Async database session used for persistence.
        """
        self._session = session

    async def create(
        self, enterprise_id: UUID, payload: StaticFinancialSnapshotCreateSchema
    ) -> StaticFinancialSnapshotModel:
        """Create and persist a static financial snapshot.

        Args:
            enterprise_id: Owning enterprise identifier.
            payload: Snapshot values and provenance metadata.

        Returns:
            The persisted snapshot.
        """
        snapshot = StaticFinancialSnapshotModel(
            enterprise_id=enterprise_id, **payload.model_dump()
        )
        self._session.add(snapshot)

        try:
            await self._session.flush()

        except IntegrityError as error:
            if 'uq_static_financial_snapshots_enterprise_id_snapshot_date' in str(
                error.orig
            ):
                raise StaticFinancialSnapshotAlreadyExistsError(
                    f'Enterprise "{enterprise_id}" already has a snapshot for '
                    f'"{payload.snapshot_date}".'
                ) from error
            raise

        await self._session.refresh(snapshot)
        return snapshot

    async def get_by_id(self, snapshot_id: UUID) -> StaticFinancialSnapshotModel | None:
        """Return a snapshot by identifier when it exists.

        Args:
            snapshot_id: Snapshot identifier.

        Returns:
            The matching snapshot, or ``None``.
        """
        result = await self._session.execute(
            select(StaticFinancialSnapshotModel).where(
                StaticFinancialSnapshotModel.id == snapshot_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(
        self, snapshot_id: UUID
    ) -> StaticFinancialSnapshotModel:
        """Return a snapshot by identifier or raise when missing.

        Args:
            snapshot_id: Snapshot identifier.

        Returns:
            The matching snapshot.

        Raises:
            StaticFinancialSnapshotNotFoundError: If no snapshot exists.
        """
        snapshot = await self.get_by_id(snapshot_id)
        if snapshot is None:
            raise StaticFinancialSnapshotNotFoundError(
                f'Static financial snapshot "{snapshot_id}" does not exist.'
            )
        return snapshot

    async def get_latest_for_date(
        self, enterprise_id: UUID, target_date: date
    ) -> StaticFinancialSnapshotModel | None:
        """Return the latest snapshot applicable to a date.

        Args:
            enterprise_id: Owning enterprise identifier.
            target_date: Latest allowed snapshot date.

        Returns:
            The newest applicable snapshot, or ``None``.
        """
        result = await self._session.execute(
            select(StaticFinancialSnapshotModel)
            .where(
                StaticFinancialSnapshotModel.enterprise_id == enterprise_id,
                StaticFinancialSnapshotModel.snapshot_date <= target_date,
            )
            .order_by(
                StaticFinancialSnapshotModel.snapshot_date.desc(),
                StaticFinancialSnapshotModel.created_at.desc(),
            )
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_for_enterprise(
        self, enterprise_id: UUID
    ) -> list[StaticFinancialSnapshotModel]:
        """List all snapshots for an enterprise.

        Args:
            enterprise_id: Owning enterprise identifier.

        Returns:
            Snapshots ordered from newest to oldest.
        """
        result = await self._session.execute(
            select(StaticFinancialSnapshotModel)
            .where(StaticFinancialSnapshotModel.enterprise_id == enterprise_id)
            .order_by(
                StaticFinancialSnapshotModel.snapshot_date.desc(),
                StaticFinancialSnapshotModel.created_at.desc(),
            )
        )
        return list(result.scalars().all())

    async def update(
        self,
        snapshot_id: UUID,
        payload: StaticFinancialSnapshotUpdateSchema,
    ) -> StaticFinancialSnapshotModel:
        """Update a static financial snapshot.

        Args:
            snapshot_id: Snapshot identifier.
            payload: Fields to update.

        Returns:
            The updated snapshot.

        Raises:
            StaticFinancialSnapshotNotFoundError: If no snapshot exists.
        """
        snapshot = await self.get_by_id_or_raise(snapshot_id)

        for field_name, field_value in payload.model_dump(exclude_unset=True).items():
            setattr(snapshot, field_name, field_value)

        await self._session.flush()
        await self._session.refresh(snapshot)
        return snapshot
