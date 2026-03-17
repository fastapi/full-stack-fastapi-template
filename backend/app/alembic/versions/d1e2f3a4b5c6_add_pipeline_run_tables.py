"""add pipeline_run and pipeline_job_run tables

Revision ID: d1e2f3a4b5c6
Revises: c9e4f7a2b8d3
Create Date: 2026-03-16

"""
from alembic import op
import sqlalchemy as sa

revision = 'd1e2f3a4b5c6'
down_revision = 'c9e4f7a2b8d3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'pipeline_run',
        sa.Column('run_id', sa.String(36), primary_key=True, nullable=False),
        sa.Column('pipeline_name', sa.String(100), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_pipeline_run_name', 'pipeline_run', ['pipeline_name'])
    op.create_index('idx_pipeline_run_status', 'pipeline_run', ['status'])

    op.create_table(
        'pipeline_job_run',
        sa.Column('run_id', sa.String(36), nullable=False),
        sa.Column('job_name', sa.String(100), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('run_id', 'job_name', name='pk_pipeline_job_run'),
    )
    op.create_index('idx_pjr_run_id', 'pipeline_job_run', ['run_id'])
    op.create_index('idx_pjr_status', 'pipeline_job_run', ['status'])


def downgrade():
    op.drop_table('pipeline_job_run')
    op.drop_table('pipeline_run')
