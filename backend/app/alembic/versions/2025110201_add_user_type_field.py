"""Add user_type field to User table

Revision ID: 2025110201
Revises: 2025010801
Create Date: 2025-11-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes

# revision identifiers, used by Alembic.
revision = '2025110201'
down_revision = '2025010801'
branch_labels = None
depends_on = None


def upgrade():
    # Add user_type column to user table with default value
    op.add_column('user', sa.Column('user_type', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False, server_default='team_member'))


def downgrade():
    # Remove user_type column from user table
    op.drop_column('user', 'user_type')

