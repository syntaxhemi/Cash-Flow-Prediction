from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from domain.ingestion.enums import (
    CredentialStatus,
    CredentialType,
    IngestionRunType,
    IngestionSourceStatus,
    IngestionStatus,
)


@dataclass(frozen=True, slots=True)
class IngestionSource:
    id: UUID
    enterprise_id: UUID
    source_key: str
    display_name: str
    status: IngestionSourceStatus
    last_synced_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class IngestionSourceCredential:
    id: UUID
    enterprise_id: UUID
    ingestion_source_id: UUID
    credential_type: CredentialType
    status: CredentialStatus
    config: dict[str, Any]
    secret_ref: str
    last_rotated_at: datetime | None
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class IngestionRun:
    id: UUID
    enterprise_id: UUID
    ingestion_source_id: UUID
    run_type: IngestionRunType
    status: IngestionStatus
    started_at: datetime | None
    finished_at: datetime | None
    records_received: int
    records_processed: int
    records_failed: int
    error_summary: str | None
    created_at: datetime
