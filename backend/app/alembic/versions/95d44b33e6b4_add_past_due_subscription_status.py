"""add_past_due_subscription_status

Revision ID: 95d44b33e6b4
Revises: c5e82d93f0b1
Create Date: 2026-03-12 22:21:23.905656

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '95d44b33e6b4'
down_revision = 'c5e82d93f0b1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PostgreSQL: add 'past_due' to the subscriptionstatus enum type
    # Note: ALTER TYPE ... ADD VALUE cannot run inside a transaction in PostgreSQL
    op.execute("ALTER TYPE subscriptionstatus ADD VALUE IF NOT EXISTS 'past_due'")


def downgrade() -> None:
    # PostgreSQL enums cannot easily remove values — this is a one-way migration.
    pass
