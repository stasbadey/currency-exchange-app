"""create deal and currency_rate tables

Revision ID: b8c9fd7b3d82
Revises: 
Create Date: 2025-09-23 12:36:06.688351

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b8c9fd7b3d82'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'currency_rates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('abbreviation', sa.String(length=8), nullable=False),
        sa.Column('scale', sa.Integer(), nullable=False),
        sa.Column('rate', sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column('rate_date', sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('currency_rates_pkey')),
        sa.UniqueConstraint(
            'rate_date', 'abbreviation', name='uq_rate_date_abbr'
        ),
    )
    op.create_table(
        'deals',
        sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
        sa.Column(
            'created_at', 
            sa.DateTime(timezone=True), 
            server_default=sa.text('now()'), 
            nullable=False,
        ),
        sa.Column(
            'amount_from', sa.Numeric(precision=18, scale=4), nullable=False
        ),
        sa.Column(
            'amount_to', sa.Numeric(precision=18, scale=4), nullable=True
        ),
        sa.Column('currency_from', sa.String(length=8), nullable=False),
        sa.Column('currency_to', sa.String(length=8), nullable=False),
        sa.Column('rate_from', sa.Float(), nullable=True),
        sa.Column('scale_from', sa.Integer(), nullable=True),
        sa.Column('rate_to', sa.Float(), nullable=True),
        sa.Column('scale_to', sa.Integer(), nullable=True),
        sa.Column(
            'status', 
            sa.Enum('PENDING', 'CONFIRMED', 'REJECTED', name='dealstatusenum'), 
            server_default='PENDING', 
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('deals_pkey')),
    )
    op.create_index(
        'deal_created_at_idx', 
        'deals', 
        [sa.text('created_at DESC')], 
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('deal_created_at_idx', table_name='deals')
    op.drop_table('deals')
    op.drop_table('currency_rates')
