"""Add UUID extension for LESMEE schema

Revision ID: 61e21c4d3142
Revises: b2374a5f43e5
Create Date: 2025-11-21 20:03:26.490669

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '61e21c4d3142'
down_revision = 'b2374a5f43e5'
branch_labels = None
depends_on = None


def upgrade():
    # Create UUID extension for UUID generation functions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')


def downgrade():
    # Note: Extensions can't be dropped if they're in use
    # This will be handled in final rollback
    pass
