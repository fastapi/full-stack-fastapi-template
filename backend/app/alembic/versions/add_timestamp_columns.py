"""Add timestamp columns to user and item tables

Revision ID: add_timestamp_columns
Revises: 1a31ce608336
Create Date: 2024-05-18 20:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'add_timestamp_columns'
down_revision = '1a31ce608336'
branch_labels = None
depends_on = None


def upgrade():
    # Add created_at and updated_at columns to user table
    op.add_column('user', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.add_column('user', sa.Column('updated_at', sa.DateTime(), nullable=True))

    # Add created_at and updated_at columns to item table
    op.add_column('item', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.add_column('item', sa.Column('updated_at', sa.DateTime(), nullable=True))


def downgrade():
    # Drop created_at and updated_at columns from item table
    op.drop_column('item', 'updated_at')
    op.drop_column('item', 'created_at')

    # Drop created_at and updated_at columns from user table
    op.drop_column('user', 'updated_at')
    op.drop_column('user', 'created_at')
