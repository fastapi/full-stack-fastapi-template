"""merge_all_heads

Revision ID: b10ccce35e94
Revises: 1a31ce608336, 6db2043f1466, 7c3ae6534636, 9c0a54914c78
Create Date: 2025-07-05 17:14:31.891148

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'b10ccce35e94'
down_revision = ('1a31ce608336', '6db2043f1466', '7c3ae6534636', '9c0a54914c78')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
