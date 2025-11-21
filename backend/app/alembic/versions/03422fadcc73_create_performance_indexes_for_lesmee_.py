"""Create performance indexes for LESMEE identity tables

Revision ID: 03422fadcc73
Revises: a4b98987c493
Create Date: 2025-11-21 20:06:44.761814

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '03422fadcc73'
down_revision = 'a4b98987c493'
branch_labels = None
depends_on = None


def upgrade():
    # Core identity indexes
    op.execute("CREATE INDEX idx_staff_user_id ON staff(user_id);")
    op.execute("CREATE INDEX idx_users_email ON users(email);")
    op.execute("CREATE INDEX idx_users_user_type ON users(user_type);")
    op.execute("CREATE INDEX idx_staff_role ON staff(role);")
    op.execute("CREATE INDEX idx_staff_availability ON staff(is_available);")
    op.execute("CREATE INDEX idx_customers_is_vip ON customers(is_vip);")


def downgrade():
    # Drop performance indexes
    indexes_to_drop = [
        'idx_customers_is_vip',
        'idx_staff_availability',
        'idx_staff_role',
        'idx_users_user_type',
        'idx_users_email',
        'idx_staff_user_id'
    ]

    for index_name in indexes_to_drop:
        op.execute(f"DROP INDEX IF EXISTS {index_name}")
