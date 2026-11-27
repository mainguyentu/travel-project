"""0002 audit logs

Revision ID: e4f1a2b3c4d5
Revises: d0ab82c5eb05
Create Date: 2026-11-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4f1a2b3c4d5'
down_revision: Union[str, None] = 'd0ab82c5eb05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('audit_logs',
    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True, nullable=False),
    sa.Column('actor_user_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=True),
    sa.Column('action', sa.String(length=80), nullable=False),
    sa.Column('entity', sa.String(length=80), nullable=False),
    sa.Column('entity_id', sa.String(length=80), nullable=True),
    sa.Column('detail', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['actor_user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_actor_user_id'), 'audit_logs', ['actor_user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_logs_actor_user_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
