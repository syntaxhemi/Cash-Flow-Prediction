from datetime import datetime
from typing import Any
from uuid import UUID

from domain.ingestion import (
    CredentialStatus,
    CredentialType,
    IngestionRunType,
    IngestionSourceStatus,
    IngestionStatus,
    IngestionUploadCleanupStatus,
)
from pydantic import Field

from schemas.base import SchemaModel


class IngestionSourceSchema(SchemaModel):
    id: UUID
    enterprise_id: UUID
    source_key: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    status: IngestionSourceStatus
    is_active: bool
    deleted_at: datetime | None = None
    last_synced_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class IngestionSourceCreateSchema(SchemaModel):
    source_key: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    status: IngestionSourceStatus = IngestionSourceStatus.ACTIVE
    is_active: bool = True


class IngestionSourceUpdateSchema(SchemaModel):
    display_name: str | None = Field(default=None, min_length=1)
    status: IngestionSourceStatus | None = None
    is_active: bool | None = None
    deleted_at: datetime | None = None
    last_synced_at: datetime | None = None


class IngestionSourceFilterParams(SchemaModel):
    source_key: str | None = Field(default=None, min_length=1)
    status: IngestionSourceStatus | None = None
    is_active: bool = True
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class IngestionSourceCredentialSchema(SchemaModel):
    """Public ingestion-source credential metadata."""

    id: UUID
    enterprise_id: UUID
    ingestion_source_id: UUID
    credential_type: CredentialType
    status: CredentialStatus
    config_json: dict[str, Any]
    last_rotated_at: datetime | None = None
    expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class IngestionSourceCredentialCreateSchema(SchemaModel):
    """Ingestion-source credential creation payload."""

    credential_type: CredentialType
    config_json: dict[str, Any] = Field(default_factory=dict)
    secret_ref: str = Field(min_length=1)
    expires_at: datetime | None = None


class IngestionSourceCredentialUpdateSchema(SchemaModel):
    """Internal ingestion-source credential persistence update payload."""

    credential_type: CredentialType | None = None
    config_json: dict[str, Any] | None = None
    secret_ref: str | None = Field(default=None, min_length=1)
    status: CredentialStatus | None = None
    last_rotated_at: datetime | None = None
    expires_at: datetime | None = None


class IngestionSourceCredentialMetadataUpdateSchema(SchemaModel):
    """Public ingestion-source credential metadata update payload."""

    credential_type: CredentialType | None = None
    config_json: dict[str, Any] | None = None
    expires_at: datetime | None = None


class IngestionSourceCredentialSecretUpdateSchema(SchemaModel):
    """Ingestion-source credential rotation payload."""

    secret_ref: str = Field(min_length=1)


class IngestionSourceCredentialFilterParams(SchemaModel):
    """Ingestion-source credential list filters."""

    credential_type: CredentialType | None = None
    status: CredentialStatus | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class IngestionRunSchema(SchemaModel):
    """Ingestion-run response schema."""

    id: UUID
    enterprise_id: UUID
    ingestion_source_id: UUID
    run_type: IngestionRunType
    status: IngestionStatus
    started_at: datetime | None = None
    finished_at: datetime | None = None
    records_received: int
    records_processed: int
    records_failed: int
    error_summary: str | None = None
    created_at: datetime


class IngestionRunCreateSchema(SchemaModel):
    """Ingestion synchronization request schema."""

    run_type: IngestionRunType = IngestionRunType.INCREMENTAL
    status: IngestionStatus = IngestionStatus.PENDING
    since: datetime | None = None


class IngestionRunUpdateSchema(SchemaModel):
    """Internal ingestion-run persistence update schema."""

    status: IngestionStatus | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    records_received: int | None = Field(default=None, ge=0)
    records_processed: int | None = Field(default=None, ge=0)
    records_failed: int | None = Field(default=None, ge=0)
    error_summary: str | None = None


class IngestionRunFilterParams(SchemaModel):
    """Ingestion-run history filters and pagination parameters."""

    status: IngestionStatus | None = None
    run_type: IngestionRunType | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class IngestionUploadCreateSchema(SchemaModel):
    """Persisted metadata for a staged ingestion upload."""

    storage_key: str = Field(min_length=1, max_length=500)
    original_filename: str = Field(min_length=1, max_length=255)
    file_format: str = Field(min_length=1, max_length=10)
    content_type: str | None = Field(default=None, max_length=100)
    size_bytes: int = Field(ge=0)
    sha256: str = Field(min_length=64, max_length=64, pattern=r'^[a-fA-F0-9]{64}$')
    sheet_name: str | None = Field(default=None, max_length=255)
    cleanup_status: IngestionUploadCleanupStatus = IngestionUploadCleanupStatus.STAGED


class IngestionUploadUpdateSchema(SchemaModel):
    """Internal staged-upload lifecycle update schema."""

    cleanup_status: IngestionUploadCleanupStatus | None = None
    cleaned_at: datetime | None = None
    cleanup_error: str | None = Field(default=None, max_length=1000)
