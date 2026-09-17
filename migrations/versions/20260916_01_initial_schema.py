"""Create monitored URL and check result tables.

Revision ID: 20260916_01
Revises:
Create Date: 2026-09-16 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "20260916_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "monitored_urls",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )
    op.create_table(
        "check_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("monitored_url_id", sa.Integer(), nullable=False),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.Column("is_up", sa.Boolean(), nullable=False),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["monitored_url_id"], ["monitored_urls.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_check_results_url_checked_at", "check_results", ["monitored_url_id", "checked_at"], unique=False
    )


def downgrade():
    op.drop_index("ix_check_results_url_checked_at", table_name="check_results")
    op.drop_table("check_results")
    op.drop_table("monitored_urls")
