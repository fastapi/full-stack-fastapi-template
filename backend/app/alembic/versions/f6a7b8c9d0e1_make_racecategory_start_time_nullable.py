"""make racecategory start_time nullable

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-04-24 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "f6a7b8c9d0e1"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("racecategory", "start_time", nullable=True)


def downgrade() -> None:
    op.execute("UPDATE racecategory SET start_time = NOW() WHERE start_time IS NULL")
    op.alter_column("racecategory", "start_time", nullable=False)
