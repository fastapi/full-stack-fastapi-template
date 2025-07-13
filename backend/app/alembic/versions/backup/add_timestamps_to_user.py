"""add_timestamps_to_user

Revision ID: add_timestamps_to_user
Revises: d98dd8ec85a3
Create Date: 2024-03-24 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = 'add_timestamps_to_user'
down_revision: Union[str, None] = 'd98dd8ec85a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add created_at and updated_at columns to user table
    op.add_column('user', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Set default values for existing rows
    op.execute("""
        UPDATE "user"
        SET created_at = NOW(),
            updated_at = NOW()
    """)
    
    # Make the columns non-nullable
    op.alter_column('user', 'created_at', nullable=False)
    op.alter_column('user', 'updated_at', nullable=False)


def downgrade() -> None:
    # Remove created_at and updated_at columns from user table
    op.drop_column('user', 'created_at')
    op.drop_column('user', 'updated_at') 