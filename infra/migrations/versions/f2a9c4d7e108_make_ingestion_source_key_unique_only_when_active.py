"""make ingestion source key unique only when active

Revision ID: f2a9c4d7e108
Revises: d7e4b9c1a602
Create Date: 2026-09-06 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2a9c4d7e108'
down_revision: Union[str, Sequence[str], None] = 'd7e4b9c1a602'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Allow a new source after the previous source was deactivated."""
    op.drop_constraint(
        'uq_ingestion_sources_enterprise_id',
        'ingestion_sources',
        type_='unique',
    )
    op.create_index(
        'uq_ingestion_sources_enterprise_id_source_key_active',
        'ingestion_sources',
        ['enterprise_id', 'source_key'],
        unique=True,
        postgresql_where=sa.text('is_active IS TRUE'),
    )


def downgrade() -> None:
    """Restore the original unconditional source-key uniqueness rule."""
    op.drop_index(
        'uq_ingestion_sources_enterprise_id_source_key_active',
        table_name='ingestion_sources',
    )
    op.create_unique_constraint(
        'uq_ingestion_sources_enterprise_id',
        'ingestion_sources',
        ['enterprise_id', 'source_key'],
    )
