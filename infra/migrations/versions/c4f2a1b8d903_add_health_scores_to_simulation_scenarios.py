"""add health scores to simulation scenarios

Revision ID: c4f2a1b8d903
Revises: 89a816ce54e9
Create Date: 2026-08-31 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c4f2a1b8d903'
down_revision: str | Sequence[str] | None = '89a816ce54e9'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        'simulation_scenarios',
        sa.Column('health_score', sa.Numeric(precision=5, scale=2), nullable=True),
    )
    op.add_column(
        'simulation_scenarios',
        sa.Column(
            'health_score_delta', sa.Numeric(precision=6, scale=2), nullable=True
        ),
    )
    op.add_column(
        'simulation_scenarios',
        sa.Column('health_status', sa.String(length=32), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('simulation_scenarios', 'health_status')
    op.drop_column('simulation_scenarios', 'health_score_delta')
    op.drop_column('simulation_scenarios', 'health_score')
