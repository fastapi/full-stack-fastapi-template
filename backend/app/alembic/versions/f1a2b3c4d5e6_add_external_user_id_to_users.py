"""Add external_user_id to users and make password_hash nullable

Revision ID: f1a2b3c4d5e6
Revises: 1a31ce608336
Create Date: 2026-02-21

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = '1a31ce608336'
branch_labels = None
depends_on = None


def upgrade():
    # Add external_user_id column for Clerk user ID mapping
    op.add_column('users', sa.Column('external_user_id', sa.String(255), nullable=True))
    op.create_index('ix_users_external_user_id', 'users', ['external_user_id'], unique=True)

    # Make password_hash nullable (Clerk users won't have one)
    op.alter_column('users', 'password_hash',
                    existing_type=sa.String(255),
                    nullable=True)


def downgrade():
    op.alter_column('users', 'password_hash',
                    existing_type=sa.String(255),
                    nullable=False)

    op.drop_index('ix_users_external_user_id', table_name='users')
    op.drop_column('users', 'external_user_id')
