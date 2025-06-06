"""merge post_privacy and cascade heads

Revision ID: feaaa16caba8
Revises: 1a31ce608336, 20250604_add_post_privacy
Create Date: 2025-06-05 12:15:19.781955

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'feaaa16caba8'
down_revision = ('1a31ce608336', '20250604_add_post_privacy')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
