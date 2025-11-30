"""add comment table

Revision ID: 2025011601
Revises: 2025011501
Create Date: 2025-01-16
"""

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "2025011601"
down_revision = "2025011501"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "comment",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("content", sqlmodel.sql.sqltypes.AutoString(length=2000), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("comment")

