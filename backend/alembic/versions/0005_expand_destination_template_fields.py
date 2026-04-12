"""expand destination fields by template

Revision ID: 0005_destination_template
Revises: 0004_destination_insight_cache
Create Date: 2026-04-11
"""

from alembic import op
import sqlalchemy as sa


revision = "0005_destination_template"
down_revision = "0004_destination_insight_cache"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("destinations", sa.Column("place_id", sa.String(length=120), nullable=True))
    op.add_column("destinations", sa.Column("rating_count", sa.BigInteger(), nullable=False, server_default="0"))
    op.add_column("destinations", sa.Column("price_raw_text", sa.Text(), nullable=True))
    op.add_column("destinations", sa.Column("open_hours_raw_text", sa.String(length=200), nullable=True))
    op.add_column("destinations", sa.Column("open_hour_open", sa.String(length=120), nullable=True))
    op.add_column("destinations", sa.Column("open_hour_close", sa.String(length=120), nullable=True))
    op.add_column("destinations", sa.Column("img_urls", sa.JSON(), nullable=True))
    op.create_index("ix_destinations_place_id", "destinations", ["place_id"], unique=False)


def downgrade():
    op.drop_index("ix_destinations_place_id", table_name="destinations")
    op.drop_column("destinations", "img_urls")
    op.drop_column("destinations", "open_hour_close")
    op.drop_column("destinations", "open_hour_open")
    op.drop_column("destinations", "open_hours_raw_text")
    op.drop_column("destinations", "price_raw_text")
    op.drop_column("destinations", "rating_count")
    op.drop_column("destinations", "place_id")
