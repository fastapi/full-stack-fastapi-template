"""add_role_to_user

Revision ID: 291237274644
Revises: fe56fa70289e
Create Date: 2026-05-19 22:19:06.452770

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '291237274644'
down_revision = 'fe56fa70289e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'user',
        sa.Column('role', sa.String(length=32), nullable=True),
    )

    op.execute("UPDATE \"user\" SET role = 'admin' WHERE is_superuser = true")
    op.execute("UPDATE \"user\" SET role = 'member' WHERE role IS NULL")

    op.alter_column('user', 'role', nullable=False)


def downgrade():
    op.drop_column('user', 'role')
