"""Add is_public field to WorkoutPost

Revision ID: 20250604_add_post_privacy
Revises: 20250601_add_user_profile_fields
Create Date: 2025-06-04 16:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250604_add_post_privacy'
down_revision = '20250601_add_user_profile_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Add is_public column to workoutpost table
    op.add_column('workoutpost', sa.Column('is_public', sa.Boolean(), nullable=False, server_default='true'))


def downgrade():
    # Remove is_public column from workoutpost table
    op.drop_column('workoutpost', 'is_public')