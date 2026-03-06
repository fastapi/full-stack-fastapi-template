"""add is_super_user to user_subscriptions

Revision ID: a3c72f81b9d0
Revises: f1fa28918ba4
Create Date: 2026-03-05

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a3c72f81b9d0'
down_revision = 'f1fa28918ba4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'user_subscriptions',
        sa.Column('is_super_user', sa.Boolean(), nullable=False, server_default='false'),
    )


def downgrade():
    op.drop_column('user_subscriptions', 'is_super_user')
