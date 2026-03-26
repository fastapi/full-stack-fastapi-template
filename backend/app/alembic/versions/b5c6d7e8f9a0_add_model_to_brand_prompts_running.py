"""add model column to brand_prompts_running work queue

Revision ID: b5c6d7e8f9a0
Revises: 1f146d860989
Create Date: 2026-03-26

brand_prompts_running is a transient work queue (no business data).
Safe to truncate. Rebuilds PK so only id is the primary key, then
adds model column and unique constraint (prompt_id, model).
"""
from alembic import op
import sqlalchemy as sa

revision = 'b5c6d7e8f9a0'
down_revision = '1f146d860989'
branch_labels = None
depends_on = None


def upgrade():
    # Safe to truncate — transient work queue; stale rows from interrupted runs are discarded.
    op.execute('TRUNCATE TABLE brand_prompts_running')

    # Fix composite PK: drop (id, prompt_id) composite, re-add single PK on id
    op.execute('ALTER TABLE brand_prompts_running DROP CONSTRAINT brand_prompts_running_pkey')
    op.execute('ALTER TABLE brand_prompts_running ADD PRIMARY KEY (id)')

    # Add model column (NOT NULL — table already truncated so no backfill needed)
    op.add_column(
        'brand_prompts_running',
        sa.Column('model', sa.String(50), nullable=False)
    )

    # Unique constraint and index
    op.create_unique_constraint(
        'uq_running_prompt_model',
        'brand_prompts_running',
        ['prompt_id', 'model']
    )
    op.create_index('idx_running_model', 'brand_prompts_running', ['model'])


def downgrade():
    op.drop_index('idx_running_model', table_name='brand_prompts_running')
    op.drop_constraint('uq_running_prompt_model', 'brand_prompts_running', type_='unique')
    op.drop_column('brand_prompts_running', 'model')
    op.execute('ALTER TABLE brand_prompts_running DROP CONSTRAINT brand_prompts_running_pkey')
    op.execute('ALTER TABLE brand_prompts_running ADD PRIMARY KEY (id, prompt_id)')
