"""Add storage_path to Attachment model

Revision ID: e62dc93fe967
Revises: 60300545fecf
Create Date: 2025-02-23 19:56:35.403358

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'e62dc93fe967'
down_revision = '60300545fecf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add storage_path column
    op.add_column('attachment', sa.Column('storage_path', sa.String(length=1024), nullable=False))


def downgrade() -> None:
    # Remove storage_path column
    op.drop_column('attachment', 'storage_path')
