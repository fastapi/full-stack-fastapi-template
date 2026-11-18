"""Add role-aware access to users.

Revision ID: c3a1e2f79b60
Revises: fe56fa70289e
Create Date: 2026-11-18 17:45:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "c3a1e2f79b60"
down_revision = "fe56fa70289e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column("role", sa.String(length=16), server_default="member", nullable=False),
    )
    op.execute("UPDATE \"user\" SET role = 'admin' WHERE is_superuser = true")
    op.drop_column("user", "is_superuser")


def downgrade() -> None:
    op.add_column(
        "user",
        sa.Column(
            "is_superuser", sa.Boolean(), server_default=sa.false(), nullable=False
        ),
    )
    op.execute("UPDATE \"user\" SET is_superuser = true WHERE role = 'admin'")
    op.drop_column("user", "role")
