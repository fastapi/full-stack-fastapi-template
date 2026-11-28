"""Replace is_superuser with role

Revision ID: b7c3d9e1f2a4
Revises: fe56fa70289e
Create Date: 2026-11-28 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7c3d9e1f2a4'
down_revision = 'fe56fa70289e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('role', sa.String(length=32), nullable=True))
    op.execute(
        "UPDATE \"user\" SET role = CASE WHEN is_superuser THEN 'admin' ELSE 'member' END"
    )
    op.alter_column('user', 'role', nullable=False)
    op.create_check_constraint(
        'ck_user_role', 'user', "role IN ('admin', 'manager', 'member')"
    )
    op.drop_column('user', 'is_superuser')


def downgrade():
    op.add_column(
        'user',
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.execute("UPDATE \"user\" SET is_superuser = (role = 'admin')")
    op.alter_column('user', 'is_superuser', server_default=None)
    op.drop_constraint('ck_user_role', 'user', type_='check')
    op.drop_column('user', 'role')
