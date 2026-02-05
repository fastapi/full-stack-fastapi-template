"""Add avatar_url to User

Revision ID: a1b2c3d4e5f6
Revises: fe56fa70289e
Create Date: 2026-02-05 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'fe56fa70289e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('avatar_url', sa.String(length=500), nullable=True))


def downgrade():
    op.drop_column('user', 'avatar_url')
