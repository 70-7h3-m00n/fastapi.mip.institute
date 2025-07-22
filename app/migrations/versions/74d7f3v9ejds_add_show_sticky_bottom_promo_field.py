"""add show_sticky_bottom field to promos table

Revision ID: 74d7f3v9ejds
Revises: 9d2f5e1a8b7c
Create Date: 2025-07-17 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "74d7f3v9ejds"
down_revision = "9d2f5e1a8b7c"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "promos",
        sa.Column(
            "show_sticky_bottom",
            sa.Boolean(),
            nullable=False,
            default=True,
            server_default=sa.text("true")
        )
    )


def downgrade():
    op.drop_column("promos", "show_sticky_bottom")
