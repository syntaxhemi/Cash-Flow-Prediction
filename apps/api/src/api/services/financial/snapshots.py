from datetime import date
from uuid import UUID

from database import IUnitOfWork
from domain.exceptions import StaticFinancialSnapshotNotFoundError
from schemas.financial import (
    StaticFinancialSnapshotCreateSchema,
    StaticFinancialSnapshotSchema,
    StaticFinancialSnapshotUpdateSchema,
)


class StaticFinancialSnapshotService:
    """Manage enterprise-scoped static forecasting features."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize the snapshot service.

        Args:
            uow: Unit of work used for snapshot and enterprise persistence.
        """
        self._uow = uow

    async def create(
        self, enterprise_id: UUID, payload: StaticFinancialSnapshotCreateSchema
    ) -> StaticFinancialSnapshotSchema:
        """Create a static financial snapshot for an enterprise.

        Args:
            enterprise_id: Owning enterprise identifier.
            payload: Snapshot values and provenance metadata.

        Returns:
            The persisted snapshot.
        """
        await self._uow.enterprises.get_active_by_id_or_raise(enterprise_id)

        if payload.ingestion_source_id is not None:
            await self._uow.ingestion_sources.get_active_by_id_or_raise(
                payload.ingestion_source_id
            )

        snapshot = await self._uow.static_financial_snapshots.create(
            enterprise_id, payload
        )
        await self._uow.commit()
        return StaticFinancialSnapshotSchema.model_validate(snapshot)

    async def get(
        self, enterprise_id: UUID, snapshot_id: UUID
    ) -> StaticFinancialSnapshotSchema:
        """Retrieve an enterprise-owned static financial snapshot.

        Args:
            enterprise_id: Owning enterprise identifier.
            snapshot_id: Snapshot identifier.

        Returns:
            The requested snapshot.

        Raises:
            StaticFinancialSnapshotNotFoundError: If the snapshot is missing or belongs
                to another enterprise.
        """
        await self._uow.enterprises.get_active_by_id_or_raise(enterprise_id)
        snapshot = await self._uow.static_financial_snapshots.get_by_id_or_raise(
            snapshot_id
        )
        if snapshot.enterprise_id != enterprise_id:
            raise StaticFinancialSnapshotNotFoundError(
                f'Static financial snapshot "{snapshot_id}" does not exist.'
            )
        return StaticFinancialSnapshotSchema.model_validate(snapshot)

    async def list(self, enterprise_id: UUID) -> list[StaticFinancialSnapshotSchema]:
        """List static financial snapshots for an enterprise.

        Args:
            enterprise_id: Owning enterprise identifier.

        Returns:
            Snapshots ordered from newest to oldest.
        """
        await self._uow.enterprises.get_active_by_id_or_raise(enterprise_id)
        snapshots = await self._uow.static_financial_snapshots.list_for_enterprise(
            enterprise_id
        )
        return [
            StaticFinancialSnapshotSchema.model_validate(item) for item in snapshots
        ]

    async def latest(
        self, enterprise_id: UUID, target_date: date
    ) -> StaticFinancialSnapshotSchema:
        """Retrieve the latest snapshot applicable to a target date.

        Args:
            enterprise_id: Owning enterprise identifier.
            target_date: Forecast or decision date.

        Returns:
            The newest snapshot dated on or before ``target_date``.

        Raises:
            StaticFinancialSnapshotNotFoundError: If no applicable snapshot exists.
        """
        await self._uow.enterprises.get_active_by_id_or_raise(enterprise_id)
        snapshot = await self._uow.static_financial_snapshots.get_latest_for_date(
            enterprise_id, target_date
        )
        if snapshot is None:
            raise StaticFinancialSnapshotNotFoundError(
                f'No static financial snapshot exists for enterprise "{enterprise_id}" '
                f'on or before "{target_date}".'
            )
        return StaticFinancialSnapshotSchema.model_validate(snapshot)

    async def update(
        self,
        enterprise_id: UUID,
        snapshot_id: UUID,
        payload: StaticFinancialSnapshotUpdateSchema,
    ) -> StaticFinancialSnapshotSchema:
        """Update an enterprise-owned static financial snapshot.

        Args:
            enterprise_id: Owning enterprise identifier.
            snapshot_id: Snapshot identifier.
            payload: Fields to update.

        Returns:
            The updated snapshot.

        Raises:
            StaticFinancialSnapshotNotFoundError: If the snapshot is missing or belongs
                to another enterprise.
        """
        await self._uow.enterprises.get_active_by_id_or_raise(enterprise_id)
        current = await self._uow.static_financial_snapshots.get_by_id_or_raise(
            snapshot_id
        )

        if current.enterprise_id != enterprise_id:
            raise StaticFinancialSnapshotNotFoundError(
                f'Static financial snapshot "{snapshot_id}" does not exist.'
            )

        if payload.ingestion_source_id is not None:
            await self._uow.ingestion_sources.get_active_by_id_or_raise(
                payload.ingestion_source_id
            )

        snapshot = await self._uow.static_financial_snapshots.update(
            snapshot_id, payload
        )
        await self._uow.commit()
        return StaticFinancialSnapshotSchema.model_validate(snapshot)
