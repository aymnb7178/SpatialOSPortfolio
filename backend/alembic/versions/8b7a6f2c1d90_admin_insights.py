"""admin insights, login history, visits, and site links

Revision ID: 8b7a6f2c1d90
Revises: d3818dbda07f
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "8b7a6f2c1d90"
down_revision: Union[str, None] = "d3818dbda07f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
    op.create_table(
        "login_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_login_events_user_id", "login_events", ["user_id"], unique=False)
    op.create_table(
        "visit_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("session_key", sa.String(length=80), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=False),
        sa.Column("user_agent", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_visit_events_user_id", "visit_events", ["user_id"], unique=False)
    op.create_index("ix_visit_events_session_key", "visit_events", ["session_key"], unique=False)
    op.create_table(
        "site_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("channel", sa.String(length=40), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("site_links")
    op.drop_index("ix_visit_events_session_key", table_name="visit_events")
    op.drop_index("ix_visit_events_user_id", table_name="visit_events")
    op.drop_table("visit_events")
    op.drop_index("ix_login_events_user_id", table_name="login_events")
    op.drop_table("login_events")
    op.drop_column("users", "last_login_at")
