"""seed the default contact links for admin management

Revision ID: 9c4d2e7f1a30
Revises: 8b7a6f2c1d90
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "9c4d2e7f1a30"
down_revision: Union[str, None] = "8b7a6f2c1d90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    links = sa.table(
        "site_links",
        sa.column("label", sa.String),
        sa.column("url", sa.String),
        sa.column("channel", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("sort_order", sa.Integer),
    )
    op.bulk_insert(links, [
        {"label": "WhatsApp", "url": "https://wa.me/966566065221", "channel": "whatsapp", "is_active": True, "sort_order": 10},
        {"label": "Telegram Personal", "url": "https://t.me/Il7IAI", "channel": "telegram", "is_active": True, "sort_order": 20},
        {"label": "X", "url": "https://x.com/uqg_9", "channel": "x", "is_active": True, "sort_order": 30},
        {"label": "Instagram", "url": "https://www.instagram.com/i1iair", "channel": "instagram", "is_active": True, "sort_order": 40},
        {"label": "Email", "url": "mailto:aymnb7178@gmail.com", "channel": "email", "is_active": True, "sort_order": 50},
    ])


def downgrade() -> None:
    op.execute("DELETE FROM site_links WHERE channel IN ('whatsapp', 'telegram', 'x', 'instagram', 'email')")
