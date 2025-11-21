"""Create LESMEE utility functions

Revision ID: e39fd2ea2f5f
Revises: e7864355f3d1
Create Date: 2025-11-21 20:03:56.523618

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'e39fd2ea2f5f'
down_revision = 'e7864355f3d1'
branch_labels = None
depends_on = None


def upgrade():
    # Function to auto-update updated_at timestamp
    op.execute("""
    CREATE OR REPLACE FUNCTION update_modified_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """)


def downgrade():
    op.execute("DROP FUNCTION IF EXISTS update_modified_column()")
