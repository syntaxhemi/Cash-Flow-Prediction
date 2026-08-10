"""create ingestion uploads

Revision ID: 7b6f3a2d1c90
Revises: 29ffaab8ba7c
Create Date: 2026-08-10 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '7b6f3a2d1c90'
down_revision: Union[str, Sequence[str], None] = '29ffaab8ba7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    cleanup_status = postgresql.ENUM(
        'staged', 'cleaned', 'failed',
        name='ingestion_upload_cleanup_status',
    )
    cleanup_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'ingestion_uploads',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('ingestion_run_id', sa.UUID(), nullable=False),
        sa.Column('storage_key', sa.String(length=500), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_format', sa.String(length=10), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=True),
        sa.Column('size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('sha256', sa.String(length=64), nullable=False),
        sa.Column('sheet_name', sa.String(length=255), nullable=True),
        sa.Column(
            'cleanup_status',
            cleanup_status,
            nullable=False,
        ),
        sa.Column(
            'cleaned_at',
            postgresql.TIMESTAMP(timezone=True),
            nullable=True,
        ),
        sa.Column('cleanup_error', sa.String(length=1000), nullable=True),
        sa.Column(
            'created_at',
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ['ingestion_run_id'],
            ['ingestion_runs.id'],
            name=op.f('fk_ingestion_uploads_ingestion_run_id_ingestion_runs'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_ingestion_uploads')),
        sa.UniqueConstraint(
            'ingestion_run_id',
            name=op.f('uq_ingestion_uploads_ingestion_run_id'),
        ),
    )
    op.create_index(
        op.f('ix_ingestion_uploads_cleanup_status'),
        'ingestion_uploads',
        ['cleanup_status'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix_ingestion_uploads_cleanup_status'),
        table_name='ingestion_uploads',
    )
    op.drop_table('ingestion_uploads')
    postgresql.ENUM(
        'staged', 'cleaned', 'failed',
        name='ingestion_upload_cleanup_status',
    ).drop(op.get_bind(), checkfirst=True)
