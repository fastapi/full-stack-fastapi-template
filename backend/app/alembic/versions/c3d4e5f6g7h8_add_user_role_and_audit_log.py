"""Add user role column and audit_log table

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-03-27 15:00:00.000000

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = "c3d4e5f6g7h8"
down_revision = "b2c3d4e5f6g7"
branch_labels = None
depends_on = None


def upgrade():
    # Add role column to user table with default 'comercial'
    op.add_column(
        "user",
        sa.Column(
            "role",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
            server_default="comercial",
        ),
    )

    # Migrate existing superusers to super_admin role
    op.execute(
        "UPDATE \"user\" SET role = 'super_admin' WHERE is_superuser = true"
    )

    # Create auditlog table
    op.create_table(
        "auditlog",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "action",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column("target_user_id", sa.Uuid(), nullable=False),
        sa.Column("performed_by_id", sa.Uuid(), nullable=False),
        sa.Column(
            "changes",
            sqlmodel.sql.sqltypes.AutoString(length=2000),
            nullable=False,
            server_default="",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["target_user_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["performed_by_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("auditlog")
    op.drop_column("user", "role")
