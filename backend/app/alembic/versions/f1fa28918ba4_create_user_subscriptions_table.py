"""create_user_subscriptions_table

Revision ID: f1fa28918ba4
Revises: f1a2b3c4d5e6
Create Date: 2026-03-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1fa28918ba4'
down_revision: Union[str, None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_subscriptions',
        sa.Column('subscription_id', sa.String(length=20), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('company_id', sa.String(length=100), nullable=True),
        sa.Column('tier', sa.Enum('free_trial', 'basic', 'pro', name='subscriptiontier'), nullable=False),
        sa.Column('status', sa.Enum('active', 'expired', 'cancelled', name='subscriptionstatus'), nullable=False),
        sa.Column('trial_started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trial_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('subscription_id'),
        sa.UniqueConstraint('user_id'),
    )
    op.create_index('idx_sub_company_id', 'user_subscriptions', ['company_id'])
    op.create_index('idx_sub_stripe_customer_id', 'user_subscriptions', ['stripe_customer_id'])
    op.create_index('idx_sub_user_id', 'user_subscriptions', ['user_id'])
    op.create_index(op.f('ix_user_subscriptions_stripe_customer_id'), 'user_subscriptions', ['stripe_customer_id'])
    op.create_index(op.f('ix_user_subscriptions_stripe_subscription_id'), 'user_subscriptions', ['stripe_subscription_id'])
    op.create_index(op.f('ix_user_subscriptions_subscription_id'), 'user_subscriptions', ['subscription_id'])
    op.create_index(op.f('ix_user_subscriptions_user_id'), 'user_subscriptions', ['user_id'])
    op.create_index(op.f('ix_user_subscriptions_company_id'), 'user_subscriptions', ['company_id'])


def downgrade() -> None:
    op.drop_index(op.f('ix_user_subscriptions_company_id'), table_name='user_subscriptions')
    op.drop_index(op.f('ix_user_subscriptions_user_id'), table_name='user_subscriptions')
    op.drop_index(op.f('ix_user_subscriptions_subscription_id'), table_name='user_subscriptions')
    op.drop_index(op.f('ix_user_subscriptions_stripe_subscription_id'), table_name='user_subscriptions')
    op.drop_index(op.f('ix_user_subscriptions_stripe_customer_id'), table_name='user_subscriptions')
    op.drop_index('idx_sub_user_id', table_name='user_subscriptions')
    op.drop_index('idx_sub_stripe_customer_id', table_name='user_subscriptions')
    op.drop_index('idx_sub_company_id', table_name='user_subscriptions')
    op.drop_table('user_subscriptions')
    op.execute("DROP TYPE IF EXISTS subscriptiontier")
    op.execute("DROP TYPE IF EXISTS subscriptionstatus")
