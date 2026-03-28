"""destination metrics

Revision ID: 0002_destination_metrics
Revises: 0001_init
Create Date: 2026-03-28
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_destination_metrics"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "destination_metrics",
        sa.Column("destination_id", sa.BigInteger(), sa.ForeignKey("destinations.id"), primary_key=True),
        sa.Column("favorite_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("rating_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("rating_sum", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("view_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade():
    op.drop_table("destination_metrics")
