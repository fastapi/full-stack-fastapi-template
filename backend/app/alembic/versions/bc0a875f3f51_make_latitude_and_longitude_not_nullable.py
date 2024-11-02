"""Make latitude and longitude not nullable

Revision ID: bc0a875f3f51
Revises: a1c01df04ba4
Create Date: 2024-11-01 22:45:19.154522

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'bc0a875f3f51'
down_revision = 'a1c01df04ba4'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
