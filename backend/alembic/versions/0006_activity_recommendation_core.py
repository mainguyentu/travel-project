"""add activity recommendation core tables

Revision ID: 0006_activity_reco_core
Revises: 0005_destination_template
Create Date: 2026-04-23
"""

from alembic import op
import sqlalchemy as sa


revision = "0006_activity_reco_core"
down_revision = "0005_destination_template"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "activities",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=160), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_activities_slug", "activities", ["slug"], unique=True)

    op.create_table(
        "destination_activities",
        sa.Column("destination_id", sa.BigInteger(), sa.ForeignKey("destinations.id"), primary_key=True),
        sa.Column("activity_id", sa.BigInteger(), sa.ForeignKey("activities.id"), primary_key=True),
        sa.Column("weight", sa.Numeric(4, 3), nullable=False, server_default="1.0"),
        sa.Column("source", sa.String(length=20), nullable=False, server_default="manual"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("weight >= 0 AND weight <= 1", name="ck_destination_activities_weight"),
    )
    op.create_index(
        "ix_destination_activities_activity_destination",
        "destination_activities",
        ["activity_id", "destination_id"],
        unique=False,
    )
    op.create_index(
        "ix_destination_activities_destination_activity",
        "destination_activities",
        ["destination_id", "activity_id"],
        unique=False,
    )

    op.create_table(
        "activity_rules",
        sa.Column("activity_id", sa.BigInteger(), sa.ForeignKey("activities.id"), primary_key=True),
        sa.Column("scenery_weight", sa.Numeric(5, 4), nullable=False, server_default="0.25"),
        sa.Column("accessibility_weight", sa.Numeric(5, 4), nullable=False, server_default="0.25"),
        sa.Column("crowd_weight", sa.Numeric(5, 4), nullable=False, server_default="0.25"),
        sa.Column("value_weight", sa.Numeric(5, 4), nullable=False, server_default="0.25"),
        sa.Column("crowd_mode", sa.String(length=20), nullable=False, server_default="prefer_low"),
        sa.Column("min_match_threshold", sa.Numeric(4, 3), nullable=False, server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "crowd_mode IN ('prefer_low', 'prefer_high')",
            name="ck_activity_rules_crowd_mode",
        ),
        sa.CheckConstraint(
            "min_match_threshold >= 0 AND min_match_threshold <= 1",
            name="ck_activity_rules_min_match_threshold",
        ),
    )
    op.create_index("ix_activity_rules_activity_id", "activity_rules", ["activity_id"], unique=False)

    op.create_table(
        "destination_features",
        sa.Column("destination_id", sa.BigInteger(), sa.ForeignKey("destinations.id"), primary_key=True),
        sa.Column("is_indoor", sa.Boolean(), nullable=True),
        sa.Column("is_outdoor", sa.Boolean(), nullable=True),
        sa.Column("suitable_time", sa.String(length=20), nullable=False, server_default="both"),
        sa.Column("budget_level", sa.String(length=20), nullable=True),
        sa.Column("duration_suggested_minutes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "suitable_time IN ('day', 'night', 'both')",
            name="ck_destination_features_suitable_time",
        ),
    )


def downgrade():
    op.drop_table("destination_features")

    op.drop_index("ix_activity_rules_activity_id", table_name="activity_rules")
    op.drop_table("activity_rules")

    op.drop_index("ix_destination_activities_destination_activity", table_name="destination_activities")
    op.drop_index("ix_destination_activities_activity_destination", table_name="destination_activities")
    op.drop_table("destination_activities")

    op.drop_index("ix_activities_slug", table_name="activities")
    op.drop_table("activities")
