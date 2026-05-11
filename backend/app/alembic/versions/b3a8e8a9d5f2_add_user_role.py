"""Add user role

Revision ID: b3a8e8a9d5f2
Revises: fe56fa70289e
Create Date: 2026-05-05 19:15:00.000000

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "b3a8e8a9d5f2"
down_revision = "fe56fa70289e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "user",
        sa.Column("role", sa.String(length=20), nullable=False, server_default="member"),
    )
    op.execute("UPDATE \"user\" SET role = 'admin' WHERE is_superuser = true")


def downgrade():
    op.drop_column("user", "role")
