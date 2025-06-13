"""Add social models for user follows and workout posts

Revision ID: 20250515_social
Revises: 
Create Date: 2025-05-15 15:56:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250515_social'
down_revision = 'd98dd8ec85a3'  # Updated to point to the previous migration
branch_labels = None
depends_on = None


def upgrade():
    # Create UserFollow table
    op.create_table(
        'userfollow',
        sa.Column('follower_id', postgresql.UUID(), nullable=False),
        sa.Column('followed_id', postgresql.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['follower_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('follower_id', 'followed_id')
    )
    
    # Create WorkoutPost table
    op.create_table(
        'workoutpost',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('workout_type', sa.String(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('calories_burned', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes for better query performance
    op.create_index(op.f('ix_workoutpost_user_id'), 'workoutpost', ['user_id'], unique=False)
    op.create_index(op.f('ix_workoutpost_created_at'), 'workoutpost', ['created_at'], unique=False)
    op.create_index(op.f('ix_userfollow_follower_id'), 'userfollow', ['follower_id'], unique=False)
    op.create_index(op.f('ix_userfollow_followed_id'), 'userfollow', ['followed_id'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_userfollow_followed_id'), table_name='userfollow')
    op.drop_index(op.f('ix_userfollow_follower_id'), table_name='userfollow')
    op.drop_index(op.f('ix_workoutpost_created_at'), table_name='workoutpost')
    op.drop_index(op.f('ix_workoutpost_user_id'), table_name='workoutpost')
    
    # Drop tables
    op.drop_table('workoutpost')
    op.drop_table('userfollow')