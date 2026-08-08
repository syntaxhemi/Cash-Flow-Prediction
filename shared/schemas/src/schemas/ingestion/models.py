from datetime import datetime
from uuid import UUID

from domain.ingestion import IngestionSourceStatus
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


class IngestionSourceFilterParams(SchemaModel):
    source_key: str | None = Field(default=None, min_length=1)
    status: IngestionSourceStatus | None = None
    is_active: bool = True
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
