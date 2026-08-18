"""Convert is_superuser to a PostgreSQL generated column derived from role.

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-08-18 18:45:00.000000

"""
import sqlalchemy as sa
from alembic import op


revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("ck_user_is_superuser_matches_role", "user", type_="check")
    op.drop_column("user", "is_superuser")
    op.execute(
        'ALTER TABLE "user" ADD COLUMN is_superuser boolean '
        "GENERATED ALWAYS AS (role = 'admin') STORED NOT NULL"
    )


def downgrade() -> None:
    op.drop_column("user", "is_superuser")
    op.add_column(
        "user",
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.execute('UPDATE "user" SET is_superuser = (role = \'admin\')')
    op.alter_column("user", "is_superuser", server_default=None)
    op.create_check_constraint(
        "ck_user_is_superuser_matches_role",
        "user",
        "(role = 'admin' AND is_superuser = true) OR "
        "(role != 'admin' AND is_superuser = false)",
    )
