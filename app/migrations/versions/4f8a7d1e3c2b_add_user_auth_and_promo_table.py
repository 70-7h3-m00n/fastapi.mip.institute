"""add user auth and promo table

Revision ID: 4f8a7d1e3c2b
Revises: a2b04b8337d1
Create Date: 2025-05-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4f8a7d1e3c2b"
down_revision = "a2b04b8337d1"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("password", sa.String(), nullable=True))
    op.add_column("users", sa.Column("role", sa.String(), nullable=False, server_default="user"))

    op.create_table(
        "promos",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("promo_code", sa.String(), nullable=False),
        sa.Column("redirect_url", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )

    op.create_index(op.f("ix_promos_id"), "promos", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_promos_id"), table_name="promos")
    op.drop_table("promos")

    op.drop_column("users", "role")
    op.drop_column("users", "password")
