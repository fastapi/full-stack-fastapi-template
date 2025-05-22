"""Add workout models for fitness tracking

Revision ID: 20250520_workout
Revises: 20250515_social
Create Date: 2025-05-20 10:38:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250520_workout'
down_revision = '20250515_social'  # Points to the previous migration
branch_labels = None
depends_on = None


def upgrade():
    # Create Workout table
    op.create_table(
        'workout',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('scheduled_date', sa.DateTime(), nullable=True),
        sa.Column('completed_date', sa.DateTime(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create Exercise table
    op.create_table(
        'exercise',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('workout_id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('sets', sa.Integer(), nullable=True),
        sa.Column('reps', sa.Integer(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workout_id'], ['workout.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes for better query performance
    op.create_index(op.f('ix_workout_user_id'), 'workout', ['user_id'], unique=False)
    op.create_index(op.f('ix_workout_scheduled_date'), 'workout', ['scheduled_date'], unique=False)
    op.create_index(op.f('ix_workout_is_completed'), 'workout', ['is_completed'], unique=False)
    op.create_index(op.f('ix_exercise_workout_id'), 'exercise', ['workout_id'], unique=False)
    op.create_index(op.f('ix_exercise_category'), 'exercise', ['category'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_exercise_category'), table_name='exercise')
    op.drop_index(op.f('ix_exercise_workout_id'), table_name='exercise')
    op.drop_index(op.f('ix_workout_is_completed'), table_name='workout')
    op.drop_index(op.f('ix_workout_scheduled_date'), table_name='workout')
    op.drop_index(op.f('ix_workout_user_id'), table_name='workout')
    
    # Drop tables
    op.drop_table('exercise')
    op.drop_table('workout')