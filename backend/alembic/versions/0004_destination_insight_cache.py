"""add insight_cache to destination_insights

Revision ID: 0004_destination_insight_cache
Revises: 0003_audit_logs
Create Date: 2026-04-08
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_destination_insight_cache"
down_revision = "0003_audit_logs"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("destination_insights", sa.Column("insight_cache", sa.JSON(), nullable=True))


def downgrade():
    op.drop_column("destination_insights", "insight_cache")
