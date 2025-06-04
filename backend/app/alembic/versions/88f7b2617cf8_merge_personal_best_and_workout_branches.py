"""merge personal best and workout branches

Revision ID: 88f7b2617cf8
Revises: 1a31ce608336, 20250520_workout
Create Date: 2025-06-03 18:28:55.689045

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '88f7b2617cf8'
down_revision = ('1a31ce608336', '20250520_workout')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
