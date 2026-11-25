"""add career journey and skills

Revision ID: b73c1d9e4f20
Revises: 8d2e4f6a7b90
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "b73c1d9e4f20"
down_revision: Union[str, None] = "8d2e4f6a7b90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("career_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("kind", sa.String(40), nullable=False, server_default="experience"),
        sa.Column("period", sa.String(120), nullable=False, server_default=""),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("title_ar", sa.String(200), nullable=False, server_default=""),
        sa.Column("organization", sa.String(200), nullable=False, server_default=""),
        sa.Column("organization_ar", sa.String(200), nullable=False, server_default=""),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("description_ar", sa.Text(), nullable=False, server_default=""),
        sa.Column("tags_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("related_projects_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_visible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
    )
    op.create_index("ix_career_entries_kind", "career_entries", ["kind"])
    op.create_table("skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("name_ar", sa.String(120), nullable=False, server_default=""),
        sa.Column("category", sa.String(80), nullable=False, server_default="technology"),
        sa.Column("category_ar", sa.String(80), nullable=False, server_default=""),
        sa.Column("level", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("description_ar", sa.Text(), nullable=False, server_default=""),
        sa.Column("related_projects_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("related_certificates_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_visible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
    )
    op.create_index("ix_skills_name", "skills", ["name"])
    op.create_index("ix_skills_category", "skills", ["category"])


def downgrade() -> None:
    op.drop_index("ix_skills_category", table_name="skills")
    op.drop_index("ix_skills_name", table_name="skills")
    op.drop_table("skills")
    op.drop_index("ix_career_entries_kind", table_name="career_entries")
    op.drop_table("career_entries")
