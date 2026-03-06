"""add trailing window metrics

Revision ID: b4d91e2f7c3a
Revises: a3c72f81b9d0
Create Date: 2026-03-06

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b4d91e2f7c3a'
down_revision = 'a3c72f81b9d0'
branch_labels = None
depends_on = None

_TABLES = (
    'brand_awareness_daily_performance',
    'brand_competitors_awareness_daily_performance',
)

_COLUMNS = (
    'trailing_window_awareness_score',
    'trailing_window_share_of_visibility',
    'trailing_window_search_share_index',
    'trailing_window_position_strength',
    'trailing_window_search_momentum',
    'trailing_window_consistency_index',
)


def upgrade():
    for table in _TABLES:
        for col in _COLUMNS:
            op.add_column(table, sa.Column(col, sa.Float(), nullable=True))


def downgrade():
    for table in _TABLES:
        for col in _COLUMNS:
            op.drop_column(table, col)
