"""Add storage_path to Attachment model

Revision ID: 2025_02_23_storage_path
Revises: 2025_02_23_gin_idx
Create Date: 2025-02-23 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2025_02_23_storage_path'
down_revision = '2025_02_23_gin_idx'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add storage_path column
    op.add_column('attachment', sa.Column('storage_path', sa.String(length=1024), nullable=False))


def downgrade() -> None:
    # Remove storage_path column
    op.drop_column('attachment', 'storage_path')
