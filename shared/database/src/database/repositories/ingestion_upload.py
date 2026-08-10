from uuid import UUID

from domain.exceptions import (
    IngestionRunNotFoundError,
    IngestionUploadAlreadyExistsError,
    IngestionUploadNotFoundError,
)
from schemas.ingestion import IngestionUploadCreateSchema, IngestionUploadUpdateSchema
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import IngestionUploadModel


class IngestionUploadRepository:
    """Persist metadata for files associated with ingestion runs."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an async database session.

        Args:
            session: Session used for persistence operations.
        """
        self._session = session

    async def create(
        self, ingestion_run_id: UUID, payload: IngestionUploadCreateSchema
    ) -> IngestionUploadModel:
        """Create and persist upload metadata for an ingestion run.

        Args:
            ingestion_run_id: Ingestion run owning the staged upload.
            payload: Validated upload metadata to persist.

        Returns:
            The persisted upload metadata model.

        Raises:
            IngestionRunNotFoundError: If the ingestion run does not exist.
            IngestionUploadAlreadyExistsError: If the run already has an upload.

        Notes:
            Unexpected integrity errors and other database errors are propagated to
            the application boundary for handling.
        """
        upload = IngestionUploadModel(
            ingestion_run_id=ingestion_run_id,
            **payload.model_dump(),
        )
        self._session.add(upload)

        try:
            await self._session.flush()

        except IntegrityError as error:
            if self._matches_constraint(
                error,
                'fk_ingestion_uploads_ingestion_run_id_ingestion_runs',
            ):
                raise IngestionRunNotFoundError(
                    f'Ingestion run "{ingestion_run_id}" does not exist.'
                ) from error
            if self._matches_constraint(
                error,
                'uq_ingestion_uploads_ingestion_run_id',
                'ingestion_uploads_ingestion_run_id_key',
            ):
                raise IngestionUploadAlreadyExistsError(
                    f'Ingestion run "{ingestion_run_id}" already has an upload.'
                ) from error
            raise

        await self._session.refresh(upload)
        return upload

    async def get_by_id(self, upload_id: UUID) -> IngestionUploadModel | None:
        """Return upload metadata by identifier when it exists.

        Args:
            upload_id: Upload identifier to query.

        Returns:
            The matching upload model, or ``None``.
        """
        result = await self._session.execute(
            select(IngestionUploadModel).where(IngestionUploadModel.id == upload_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(self, upload_id: UUID) -> IngestionUploadModel:
        """Return upload metadata or raise when it is missing.

        Args:
            upload_id: Upload identifier to query.

        Returns:
            The matching upload model.

        Raises:
            IngestionUploadNotFoundError: If no upload exists.
        """
        upload = await self.get_by_id(upload_id)
        if upload is None:
            raise IngestionUploadNotFoundError(
                f'Ingestion upload "{upload_id}" does not exist.'
            )
        return upload

    async def get_by_run_id(self, run_id: UUID) -> IngestionUploadModel | None:
        """Return upload metadata associated with an ingestion run.

        Args:
            run_id: Ingestion run identifier to query.

        Returns:
            The matching upload model, or ``None`` when the run has no upload.
        """
        result = await self._session.execute(
            select(IngestionUploadModel).where(
                IngestionUploadModel.ingestion_run_id == run_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_run_id_or_raise(self, run_id: UUID) -> IngestionUploadModel:
        """Return a run's upload metadata or raise when it is missing.

        Args:
            run_id: Ingestion run identifier to query.

        Returns:
            The upload model associated with the run.

        Raises:
            IngestionUploadNotFoundError: If the run has no upload metadata.
        """
        upload = await self.get_by_run_id(run_id)
        if upload is None:
            raise IngestionUploadNotFoundError(
                f'No ingestion upload exists for run "{run_id}".'
            )
        return upload

    async def update(
        self, upload_id: UUID, payload: IngestionUploadUpdateSchema
    ) -> IngestionUploadModel:
        """Update persisted upload metadata.

        Args:
            upload_id: Upload identifier to update.
            payload: Validated upload fields to change.

        Returns:
            The updated upload model.

        Raises:
            IngestionUploadNotFoundError: If no upload exists.
        """
        upload = await self.get_by_id_or_raise(upload_id)

        for field_name, field_value in payload.model_dump(exclude_unset=True).items():
            setattr(upload, field_name, field_value)

        await self._session.flush()
        await self._session.refresh(upload)
        return upload

    @staticmethod
    def _matches_constraint(error: IntegrityError, *constraint_names: str) -> bool:
        """Return whether an integrity error references a known constraint.

        Args:
            error: Integrity error raised by the database.
            *constraint_names: Constraint names to match.

        Returns:
            ``True`` when the error references one of the supplied constraints.
        """
        error_message = str(error.orig)
        return any(name in error_message for name in constraint_names)
