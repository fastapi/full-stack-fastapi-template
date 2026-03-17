"""change awareness daily performance pk

Revision ID: c9e4f7a2b8d3
Revises: b3f1cc820a11
Create Date: 2026-03-16

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'c9e4f7a2b8d3'
down_revision = 'b3f1cc820a11'
branch_labels = None
depends_on = None


def upgrade():
    # --- brand_awareness_daily_performance ---
    op.execute('ALTER TABLE brand_awareness_daily_performance DROP CONSTRAINT brand_awareness_daily_performance_pkey')
    op.execute('ALTER TABLE brand_awareness_daily_performance DROP COLUMN id')
    op.execute('ALTER TABLE brand_awareness_daily_performance RENAME COLUMN created_date TO search_date')
    op.execute('ALTER TABLE brand_awareness_daily_performance ADD PRIMARY KEY (brand_id, segment, search_date)')

    # --- brand_competitors_awareness_daily_performance ---
    op.execute('ALTER TABLE brand_competitors_awareness_daily_performance DROP CONSTRAINT brand_competitors_awareness_daily_performance_pkey')
    op.execute('ALTER TABLE brand_competitors_awareness_daily_performance DROP COLUMN id')
    op.execute('ALTER TABLE brand_competitors_awareness_daily_performance RENAME COLUMN created_date TO search_date')
    op.execute('ALTER TABLE brand_competitors_awareness_daily_performance ADD PRIMARY KEY (search_target_brand_id, competitor_brand_name, segment, search_date)')


def downgrade():
    # --- brand_competitors_awareness_daily_performance ---
    op.execute('ALTER TABLE brand_competitors_awareness_daily_performance DROP CONSTRAINT brand_competitors_awareness_daily_performance_pkey')
    op.execute('ALTER TABLE brand_competitors_awareness_daily_performance RENAME COLUMN search_date TO created_date')
    op.execute('ALTER TABLE brand_competitors_awareness_daily_performance ADD COLUMN id SERIAL')
    op.execute('ALTER TABLE brand_competitors_awareness_daily_performance ADD PRIMARY KEY (id)')

    # --- brand_awareness_daily_performance ---
    op.execute('ALTER TABLE brand_awareness_daily_performance DROP CONSTRAINT brand_awareness_daily_performance_pkey')
    op.execute('ALTER TABLE brand_awareness_daily_performance RENAME COLUMN search_date TO created_date')
    op.execute('ALTER TABLE brand_awareness_daily_performance ADD COLUMN id SERIAL')
    op.execute('ALTER TABLE brand_awareness_daily_performance ADD PRIMARY KEY (id)')
