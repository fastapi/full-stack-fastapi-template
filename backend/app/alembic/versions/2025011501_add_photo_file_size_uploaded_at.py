"""add file_size and uploaded_at to photo table

Revision ID: 2025011501
Revises: 2025111201
Create Date: 2025-01-15
"""

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2025011501"
down_revision = "2025111201"
branch_labels = None
depends_on = None


def upgrade():
    # Add file_size column (in bytes, default 0 for existing photos)
    op.add_column("photo", sa.Column("file_size", sa.Integer(), nullable=False, server_default="0"))
    
    # Add uploaded_at column (use created_at as default for existing photos)
    # First add as nullable, then update existing rows, then make non-nullable
    op.add_column("photo", sa.Column("uploaded_at", sa.DateTime(), nullable=True))
    op.execute("UPDATE photo SET uploaded_at = created_at WHERE uploaded_at IS NULL")
    op.alter_column("photo", "uploaded_at", nullable=False)


def downgrade():
    op.drop_column("photo", "uploaded_at")
    op.drop_column("photo", "file_size")

