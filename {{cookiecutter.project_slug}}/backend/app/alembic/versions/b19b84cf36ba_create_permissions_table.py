"""create permissions table

Revision ID: b19b84cf36ba
Revises: c44979891d61
Create Date: 2023-04-18 09:00:07.199521

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b19b84cf36ba'
down_revision = 'c44979891d61'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "permission",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("object", sa.String(), nullable=False),
        sa.Column("permissions", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["role_id"], ["role.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_permission_id"), "permission", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_permission_id"), table_name="permission")
    op.drop_table("permission")
