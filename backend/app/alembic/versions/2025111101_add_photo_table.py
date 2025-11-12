"""add photo table

Revision ID: 2025111101
Revises: 2025110302
Create Date: 2025-11-11
"""

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "2025111101"
down_revision = "2025110302"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "photo",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("filename", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("url", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("gallery_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["gallery_id"], ["gallery.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("photo")


