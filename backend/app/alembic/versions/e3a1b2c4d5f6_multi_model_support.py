"""add multi-model support: model + model_sources columns to aggregation tables

Revision ID: e3a1b2c4d5f6
Revises: d1e2f3a4b5c6
Create Date: 2026-03-17

Adds model and model_sources columns to the four aggregation tables and
target_models to brand_prompts. Reconstructs composite primary keys to
include model. Backfills existing rows with model='all' (already set by
server_default) and model_sources='["gemini"]' (all legacy data is Gemini-only).
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'e3a1b2c4d5f6'
down_revision = 'd1e2f3a4b5c6'
branch_labels = None
depends_on = None


def upgrade():
    # ── brand_search_basic_metrics_daily ────────────────────────────────────
    op.add_column('brand_search_basic_metrics_daily',
        sa.Column('model', sa.String(50), nullable=False, server_default='all'))
    op.add_column('brand_search_basic_metrics_daily',
        sa.Column('model_sources', sa.Text(), nullable=True))
    op.execute(
        'ALTER TABLE brand_search_basic_metrics_daily '
        'DROP CONSTRAINT pk_brand_segment_time_window'
    )
    op.execute(
        'ALTER TABLE brand_search_basic_metrics_daily '
        'ADD CONSTRAINT pk_brand_segment_time_window '
        'PRIMARY KEY (search_target_brand_id, segment, search_date_start, search_date_end, model)'
    )
    op.execute(
        "UPDATE brand_search_basic_metrics_daily "
        "SET model_sources = '[\"gemini\"]' WHERE model = 'all'"
    )

    # ── brand_awareness_daily_performance ────────────────────────────────────
    op.add_column('brand_awareness_daily_performance',
        sa.Column('model', sa.String(50), nullable=False, server_default='all'))
    op.add_column('brand_awareness_daily_performance',
        sa.Column('model_sources', sa.Text(), nullable=True))
    op.execute(
        'ALTER TABLE brand_awareness_daily_performance '
        'DROP CONSTRAINT brand_awareness_daily_performance_pkey'
    )
    op.execute(
        'ALTER TABLE brand_awareness_daily_performance '
        'ADD PRIMARY KEY (brand_id, segment, search_date, model)'
    )
    op.execute(
        "UPDATE brand_awareness_daily_performance "
        "SET model_sources = '[\"gemini\"]' WHERE model = 'all'"
    )

    # ── brand_competitors_daily_basic_metrics ────────────────────────────────
    op.add_column('brand_competitors_daily_basic_metrics',
        sa.Column('model', sa.String(50), nullable=False, server_default='all'))
    op.add_column('brand_competitors_daily_basic_metrics',
        sa.Column('model_sources', sa.Text(), nullable=True))
    op.execute(
        'ALTER TABLE brand_competitors_daily_basic_metrics '
        'DROP CONSTRAINT pk_brand_segment_competitor_time_window'
    )
    op.execute(
        'ALTER TABLE brand_competitors_daily_basic_metrics '
        'ADD CONSTRAINT pk_brand_segment_competitor_time_window '
        'PRIMARY KEY (search_target_brand_id, segment, competitor_brand_name, '
        'search_date_start, search_date_end, model)'
    )
    op.execute(
        "UPDATE brand_competitors_daily_basic_metrics "
        "SET model_sources = '[\"gemini\"]' WHERE model = 'all'"
    )

    # ── brand_competitors_awareness_daily_performance ────────────────────────
    op.add_column('brand_competitors_awareness_daily_performance',
        sa.Column('model', sa.String(50), nullable=False, server_default='all'))
    op.add_column('brand_competitors_awareness_daily_performance',
        sa.Column('model_sources', sa.Text(), nullable=True))
    op.execute(
        'ALTER TABLE brand_competitors_awareness_daily_performance '
        'DROP CONSTRAINT brand_competitors_awareness_daily_performance_pkey'
    )
    op.execute(
        'ALTER TABLE brand_competitors_awareness_daily_performance '
        'ADD PRIMARY KEY (search_target_brand_id, competitor_brand_name, segment, search_date, model)'
    )
    op.execute(
        "UPDATE brand_competitors_awareness_daily_performance "
        "SET model_sources = '[\"gemini\"]' WHERE model = 'all'"
    )

    # ── brand_prompts ────────────────────────────────────────────────────────
    op.add_column('brand_prompts',
        sa.Column('target_models', sa.Text(), nullable=True))


def downgrade():
    # Remove target_models from brand_prompts
    op.drop_column('brand_prompts', 'target_models')

    # brand_competitors_awareness_daily_performance
    op.execute(
        'ALTER TABLE brand_competitors_awareness_daily_performance '
        'DROP CONSTRAINT brand_competitors_awareness_daily_performance_pkey'
    )
    op.execute(
        'ALTER TABLE brand_competitors_awareness_daily_performance '
        'ADD PRIMARY KEY (search_target_brand_id, competitor_brand_name, segment, search_date)'
    )
    op.drop_column('brand_competitors_awareness_daily_performance', 'model_sources')
    op.drop_column('brand_competitors_awareness_daily_performance', 'model')

    # brand_competitors_daily_basic_metrics
    op.execute(
        'ALTER TABLE brand_competitors_daily_basic_metrics '
        'DROP CONSTRAINT pk_brand_segment_competitor_time_window'
    )
    op.execute(
        'ALTER TABLE brand_competitors_daily_basic_metrics '
        'ADD CONSTRAINT pk_brand_segment_competitor_time_window '
        'PRIMARY KEY (search_target_brand_id, segment, competitor_brand_name, '
        'search_date_start, search_date_end)'
    )
    op.drop_column('brand_competitors_daily_basic_metrics', 'model_sources')
    op.drop_column('brand_competitors_daily_basic_metrics', 'model')

    # brand_awareness_daily_performance
    op.execute(
        'ALTER TABLE brand_awareness_daily_performance '
        'DROP CONSTRAINT brand_awareness_daily_performance_pkey'
    )
    op.execute(
        'ALTER TABLE brand_awareness_daily_performance '
        'ADD PRIMARY KEY (brand_id, segment, search_date)'
    )
    op.drop_column('brand_awareness_daily_performance', 'model_sources')
    op.drop_column('brand_awareness_daily_performance', 'model')

    # brand_search_basic_metrics_daily
    op.execute(
        'ALTER TABLE brand_search_basic_metrics_daily '
        'DROP CONSTRAINT pk_brand_segment_time_window'
    )
    op.execute(
        'ALTER TABLE brand_search_basic_metrics_daily '
        'ADD CONSTRAINT pk_brand_segment_time_window '
        'PRIMARY KEY (search_target_brand_id, segment, search_date_start, search_date_end)'
    )
    op.drop_column('brand_search_basic_metrics_daily', 'model_sources')
    op.drop_column('brand_search_basic_metrics_daily', 'model')
