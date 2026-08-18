"""Keep is_superuser consistent with role via check constraint.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-18 18:30:00.000000

"""
from alembic import op


revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        'UPDATE "user" SET is_superuser = (role = \'admin\') WHERE '
        "(role = 'admin' AND is_superuser = false) OR "
        "(role != 'admin' AND is_superuser = true)"
    )
    op.create_check_constraint(
        "ck_user_is_superuser_matches_role",
        "user",
        "(role = 'admin' AND is_superuser = true) OR "
        "(role != 'admin' AND is_superuser = false)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_user_is_superuser_matches_role", "user", type_="check")
