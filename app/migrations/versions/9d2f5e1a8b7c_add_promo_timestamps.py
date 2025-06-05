"""add promo timestamps

Revision ID: 9d2f5e1a8b7c
Revises: 4f8a7d1e3c2b
Create Date: 2025-06-05 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9d2f5e1a8b7c"
down_revision = "4f8a7d1e3c2b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "promos",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now()
        )
    )
    op.add_column(
        "promos",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now()
        )
    )


def downgrade():
    # Remove created_at and updated_at columns from promos table
    op.drop_column("promos", "updated_at")
    op.drop_column("promos", "created_at")
