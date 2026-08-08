"""add ingestion source soft deletion

Revision ID: 29ffaab8ba7c
Revises: 4a2c03181126
Create Date: 2026-08-08 18:40:26.235693
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '29ffaab8ba7c'
down_revision: Union[str, Sequence[str], None] = '4a2c03181126'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'ingestion_sources',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        'ingestion_sources',
        sa.Column(
            'deleted_at', postgresql.TIMESTAMP(timezone=True), nullable=True
        ),
    )
    op.alter_column('ingestion_sources', 'is_active', server_default=None)


def downgrade() -> None:
    op.drop_column('ingestion_sources', 'deleted_at')
    op.drop_column('ingestion_sources', 'is_active')
