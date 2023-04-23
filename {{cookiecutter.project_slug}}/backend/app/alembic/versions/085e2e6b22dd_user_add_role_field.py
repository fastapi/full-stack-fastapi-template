"""user add role field

Revision ID: 085e2e6b22dd
Revises: b19b84cf36ba
Create Date: 2023-04-18 11:42:43.587312

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '085e2e6b22dd'
down_revision = 'b19b84cf36ba'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user',
        sa.Column('role_id', sa.Integer(), nullable=True),
    )
    op.create_foreign_key('fk_role_user', 'user', 'role', ['role_id'], ['id'])


def downgrade():
    pass
