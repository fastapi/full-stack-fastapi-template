"""Add user role column

Revision ID: a1b2c3d4e5f6
Revises: fe56fa70289e
Create Date: 2026-08-18 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "a1b2c3d4e5f6"
down_revision = "fe56fa70289e"
branch_labels = None
depends_on = None

user_role_enum = sa.Enum("admin", "manager", "member", name="userrole")


def upgrade() -> None:
    bind = op.get_bind()
    user_role_enum.create(bind, checkfirst=True)
    op.add_column(
        "user",
        sa.Column(
            "role",
            user_role_enum,
            nullable=False,
            server_default="member",
        ),
    )
    op.execute('UPDATE "user" SET role = \'admin\' WHERE is_superuser = true')
    op.alter_column("user", "role", server_default=None)


def downgrade() -> None:
    op.drop_column("user", "role")
    user_role_enum.drop(op.get_bind(), checkfirst=True)
