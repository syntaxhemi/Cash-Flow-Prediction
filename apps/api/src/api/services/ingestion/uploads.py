import hashlib
from pathlib import Path
from typing import ClassVar
from uuid import uuid4

from domain.exceptions import InvalidIngestionRunError
from fastapi import UploadFile
from schemas.ingestion import IngestionUploadCreateSchema


class UploadStagingService:
    """Stage uploaded accounting files for asynchronous worker processing."""

    _EXPECTED_SUFFIXES: ClassVar[dict[str, str]] = {'csv': '.csv', 'excel': '.xlsx'}
    _ALLOWED_CONTENT_TYPES: ClassVar[dict[str, set[str]]] = {
        'csv': {'text/csv', 'text/plain', 'application/csv'},
        'excel': {
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/octet-stream',
        },
    }
    _CHUNK_SIZE: ClassVar[int] = 1024 * 1024

    def __init__(self, directory: str, max_bytes: int) -> None:
        """Initialize upload staging configuration.

        Args:
            directory: Shared directory mounted by API and worker processes.
            max_bytes: Maximum accepted upload size.
        """
        self._directory = Path(directory)
        self._max_bytes = max_bytes

    async def stage(
        self,
        upload: UploadFile,
        file_format: str,
        sheet_name: str | None = None,
    ) -> IngestionUploadCreateSchema:
        """Stage one upload and return its persisted metadata.

        Args:
            upload: Multipart file received from the API request.
            file_format: Configured source format, either ``csv`` or ``excel``.
            sheet_name: Optional Excel worksheet name.

        Returns:
            Validated metadata for the staged file.

        Raises:
            InvalidIngestionRunError: If the file metadata or size is invalid.
        """
        suffix = self._EXPECTED_SUFFIXES.get(file_format)
        if suffix is None:
            raise InvalidIngestionRunError(
                f'Unsupported file ingestion format "{file_format}".'
            )

        original_filename = Path(upload.filename or '').name
        if not original_filename:
            raise InvalidIngestionRunError('Uploaded file must have a filename.')
        if Path(original_filename).suffix.lower() != suffix:
            raise InvalidIngestionRunError(
                f'{file_format} ingestion requires files with a {suffix} extension.'
            )
        if upload.content_type not in self._ALLOWED_CONTENT_TYPES[file_format]:
            raise InvalidIngestionRunError(
                f'Unsupported content type for {file_format} upload.'
            )

        self._directory.mkdir(parents=True, exist_ok=True)
        storage_key = f'{uuid4().hex}{suffix}'
        destination = self._directory / storage_key
        digest = hashlib.sha256()
        size_bytes = 0

        try:
            await upload.seek(0)
            with destination.open('wb') as file:
                while chunk := await upload.read(self._CHUNK_SIZE):
                    size_bytes += len(chunk)
                    if size_bytes > self._max_bytes:
                        raise InvalidIngestionRunError(
                            f'Uploaded file exceeds the {self._max_bytes} byte limit.'
                        )
                    digest.update(chunk)
                    file.write(chunk)
        except Exception:
            destination.unlink(missing_ok=True)
            raise

        if size_bytes == 0:
            destination.unlink(missing_ok=True)
            raise InvalidIngestionRunError('Uploaded file must not be empty.')

        return IngestionUploadCreateSchema(
            storage_key=storage_key,
            original_filename=original_filename,
            file_format=file_format,
            content_type=upload.content_type,
            size_bytes=size_bytes,
            sha256=digest.hexdigest(),
            sheet_name=sheet_name,
        )
