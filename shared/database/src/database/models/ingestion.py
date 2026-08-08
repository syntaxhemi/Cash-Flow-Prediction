from datetime import datetime
from uuid import UUID, uuid4

from domain.ingestion import (
    CredentialStatus,
    CredentialType,
    IngestionRunType,
    IngestionSourceStatus,
    IngestionStatus,
)
from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database.base import Base
from database.models.enterprise import EnterpriseModel
from database.utils import enum_type


class IngestionSourceModel(Base):
    __tablename__ = 'ingestion_sources'
    __table_args__ = (UniqueConstraint('enterprise_id', 'source_key'),)

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    enterprise_id: Mapped[UUID] = mapped_column(
        ForeignKey('enterprises.id'), nullable=False
    )
    source_key: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[IngestionSourceStatus] = mapped_column(
        enum_type(IngestionSourceStatus, name='ingestion_source_status'), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    last_synced_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    enterprise: Mapped[EnterpriseModel] = relationship(
        back_populates='ingestion_sources'
    )
    credentials: Mapped[list['IngestionSourceCredentialModel']] = relationship(
        back_populates='ingestion_source'
    )


class IngestionSourceCredentialModel(Base):
    __tablename__ = 'ingestion_source_credentials'
    __table_args__ = (
        Index('ix_ingestion_source_credentials_enterprise_id', 'enterprise_id'),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    enterprise_id: Mapped[UUID] = mapped_column(
        ForeignKey('enterprises.id'), nullable=False
    )
    ingestion_source_id: Mapped[UUID] = mapped_column(
        ForeignKey('ingestion_sources.id'), nullable=False
    )
    credential_type: Mapped[CredentialType] = mapped_column(
        enum_type(CredentialType, name='credential_type'), nullable=False
    )
    status: Mapped[CredentialStatus] = mapped_column(
        enum_type(CredentialStatus, name='credential_status'), nullable=False
    )
    config_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    secret_ref: Mapped[str] = mapped_column(String(500), nullable=False)
    last_rotated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    enterprise: Mapped[EnterpriseModel] = relationship(back_populates='credentials')
    ingestion_source: Mapped[IngestionSourceModel] = relationship(
        back_populates='credentials'
    )


class IngestionRunModel(Base):
    __tablename__ = 'ingestion_runs'
    __table_args__ = (Index('ix_ingestion_runs_enterprise_id', 'enterprise_id'),)

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    enterprise_id: Mapped[UUID] = mapped_column(
        ForeignKey('enterprises.id'), nullable=False
    )
    ingestion_source_id: Mapped[UUID] = mapped_column(
        ForeignKey('ingestion_sources.id'), nullable=False
    )
    run_type: Mapped[IngestionRunType] = mapped_column(
        enum_type(IngestionRunType, name='ingestion_run_type'), nullable=False
    )
    status: Mapped[IngestionStatus] = mapped_column(
        enum_type(IngestionStatus, name='ingestion_status'), nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    records_received: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_summary: Mapped[str | None] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    enterprise: Mapped[EnterpriseModel] = relationship()
    ingestion_source: Mapped[IngestionSourceModel] = relationship()
