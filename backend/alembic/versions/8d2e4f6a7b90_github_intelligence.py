"""add github intelligence cache

Revision ID: 8d2e4f6a7b90
Revises: 4f9d7c2a1b30
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "8d2e4f6a7b90"
down_revision: Union[str, None] = "4f9d7c2a1b30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "github_repositories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("github_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("html_url", sa.String(1000), nullable=False),
        sa.Column("homepage", sa.String(1000), nullable=False, server_default=""),
        sa.Column("language", sa.String(80), nullable=False, server_default=""),
        sa.Column("languages_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("topics_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("readme_markdown", sa.Text(), nullable=False, server_default=""),
        sa.Column("stars", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("forks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("watchers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("open_issues", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("size_kb", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("default_branch", sa.String(160), nullable=False, server_default="main"),
        sa.Column("created_at_github", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at_github", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pushed_at_github", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_fork", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_visible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("synced_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.UniqueConstraint("github_id"),
        sa.UniqueConstraint("full_name"),
    )
    op.create_index("ix_github_repositories_github_id", "github_repositories", ["github_id"], unique=True)
    op.create_index("ix_github_repositories_name", "github_repositories", ["name"], unique=False)
    op.create_index("ix_github_repositories_full_name", "github_repositories", ["full_name"], unique=True)
    op.create_table(
        "github_sync_state",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(80), nullable=False),
        sa.Column("profile_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("activity_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("language_totals_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rate_limit_remaining", sa.Integer(), nullable=True),
        sa.Column("rate_limit_reset_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=False, server_default=""),
        sa.UniqueConstraint("username"),
    )


def downgrade() -> None:
    op.drop_table("github_sync_state")
    op.drop_index("ix_github_repositories_full_name", table_name="github_repositories")
    op.drop_index("ix_github_repositories_name", table_name="github_repositories")
    op.drop_index("ix_github_repositories_github_id", table_name="github_repositories")
    op.drop_table("github_repositories")
