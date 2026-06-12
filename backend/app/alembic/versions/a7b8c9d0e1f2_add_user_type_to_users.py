"""add user_type to users

Revision ID: a7b8c9d0e1f2
Revises: f1a2b3c4d5e6
Create Date: 2026-06-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7b8c9d0e1f2'
down_revision = 'f1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'users',
        sa.Column(
            'user_type',
            sa.String(length=20),
            nullable=False,
            server_default='normal',
        ),
    )
    # Existing superusers become admins
    op.execute("UPDATE users SET user_type = 'admin' WHERE is_superuser")
    op.create_index(op.f('ix_users_user_type'), 'users', ['user_type'])


def downgrade():
    op.drop_index(op.f('ix_users_user_type'), table_name='users')
    op.drop_column('users', 'user_type')
