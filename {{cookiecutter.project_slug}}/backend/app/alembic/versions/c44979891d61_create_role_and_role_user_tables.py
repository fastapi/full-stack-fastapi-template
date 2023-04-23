"""create role and role_user tables

Revision ID: c44979891d61
Revises: d4867f3a4c0a
Create Date: 2023-04-18 08:57:49.843129

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c44979891d61'
down_revision = 'd4867f3a4c0a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_role_id"), "role", ["id"], unique=False)
    # op.create_table(
    #     "role_user",
    #     sa.Column("id", sa.Integer(), nullable=False),
    #     sa.Column("user_id", sa.Integer(), nullable=False),
    #     sa.Column("role_id", sa.Integer(), nullable=False),
    #     sa.ForeignKeyConstraint(["role_id"], ["role.id"], ),
    #     sa.ForeignKeyConstraint(["user_id"], ["user.id"], ),
    #     sa.PrimaryKeyConstraint("id"),
    # )
    # op.create_index(op.f("ix_role_user_id"), "role_user", ["id"], unique=False)
    # op.create_index(op.f("ix_role_user_role_id"), "role_user", ["role_id"], unique=False)
    # op.create_index(op.f("ix_role_user_user_id"), "role_user", ["user_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_role_id"), table_name="role")
    op.drop_table("role")
    op.drop_index(op.f("ix_role_user_id"), table_name="role_user")
    op.drop_index(op.f("ix_role_user_role_id"), table_name="role_user")
    op.drop_index(op.f("ix_role_user_user_id"), table_name="role_user")
    op.drop_table("role_user")
