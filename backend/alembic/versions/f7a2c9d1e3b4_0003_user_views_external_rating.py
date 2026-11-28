"""0003 user views + external rating

Revision ID: f7a2c9d1e3b4
Revises: e4f1a2b3c4d5
Create Date: 2026-11-28

- user_views: thói quen xem per-user (recommendation input).
- destinations.external_*: điểm tổng hợp từ nguồn chính thống (nhập tay qua bulk).

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f7a2c9d1e3b4'
down_revision: Union[str, None] = 'e4f1a2b3c4d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_views',
        sa.Column('user_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
        sa.Column('destination_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
        sa.Column('view_count', sa.Integer(), server_default='1', nullable=False),
        sa.Column('last_viewed_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'destination_id'),
    )
    op.create_index('ix_user_views_user_id', 'user_views', ['user_id'], unique=False)
    op.add_column('destinations', sa.Column('external_rating_avg', sa.Numeric(3, 2), server_default='0', nullable=False))
    op.add_column('destinations', sa.Column('external_rating_count', sa.BigInteger(), server_default='0', nullable=False))
    op.add_column('destinations', sa.Column('external_source', sa.String(80), server_default='manual', nullable=False))


def downgrade() -> None:
    op.drop_column('destinations', 'external_source')
    op.drop_column('destinations', 'external_rating_count')
    op.drop_column('destinations', 'external_rating_avg')
    op.drop_index('ix_user_views_user_id', table_name='user_views')
    op.drop_table('user_views')
