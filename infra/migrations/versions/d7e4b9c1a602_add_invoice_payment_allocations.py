"""add invoice payment allocations

Revision ID: d7e4b9c1a602
Revises: c4f2a1b8d903
Create Date: 2026-09-05 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = 'd7e4b9c1a602'
down_revision: str | Sequence[str] | None = 'c4f2a1b8d903'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the invoice-to-payment allocation table."""
    op.create_table(
        'invoice_payment_allocations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('enterprise_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            'payment_transaction_id', postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column(
            'allocated_amount', sa.Numeric(precision=19, scale=4), nullable=False
        ),
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
        sa.CheckConstraint(
            'allocated_amount > 0',
            name='ck_invoice_payment_allocations_amount_positive',
        ),
        sa.ForeignKeyConstraint(
            ['enterprise_id'],
            ['enterprises.id'],
            name=op.f('fk_invoice_payment_allocations_enterprise_id_enterprises'),
        ),
        sa.ForeignKeyConstraint(
            ['invoice_id'],
            ['financial_transactions.id'],
            name=op.f(
                'fk_invoice_payment_allocations_invoice_id_financial_transactions'
            ),
        ),
        sa.ForeignKeyConstraint(
            ['payment_transaction_id'],
            ['financial_transactions.id'],
            name=op.f(
                'fk_invoice_payment_allocations_payment_transaction_id_financial_transactions'
            ),
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_invoice_payment_allocations')),
        sa.UniqueConstraint(
            'invoice_id',
            'payment_transaction_id',
            name=op.f('uq_invoice_payment_allocations_invoice_id'),
        ),
    )
    op.create_index(
        'ix_invoice_payment_allocations_enterprise_invoice_id',
        'invoice_payment_allocations',
        ['enterprise_id', 'invoice_id'],
        unique=False,
    )
    op.create_index(
        'ix_invoice_payment_allocations_enterprise_payment_id',
        'invoice_payment_allocations',
        ['enterprise_id', 'payment_transaction_id'],
        unique=False,
    )


def downgrade() -> None:
    """Drop invoice-to-payment allocations."""
    op.drop_index(
        'ix_invoice_payment_allocations_enterprise_payment_id',
        table_name='invoice_payment_allocations',
    )
    op.drop_index(
        'ix_invoice_payment_allocations_enterprise_invoice_id',
        table_name='invoice_payment_allocations',
    )
    op.drop_table('invoice_payment_allocations')
