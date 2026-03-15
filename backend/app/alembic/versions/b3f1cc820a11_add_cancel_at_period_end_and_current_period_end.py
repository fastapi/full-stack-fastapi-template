"""add cancel_at_period_end and current_period_end to user_subscriptions

Revision ID: b3f1cc820a11
Revises: 95d44b33e6b4
Create Date: 2026-03-14

"""
from alembic import op
import sqlalchemy as sa

revision = 'b3f1cc820a11'
down_revision = '95d44b33e6b4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'user_subscriptions',
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        'user_subscriptions',
        sa.Column('cancel_at_period_end', sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade():
    op.drop_column('user_subscriptions', 'cancel_at_period_end')
    op.drop_column('user_subscriptions', 'current_period_end')
