"""Create LESMEE Users table with INT primary key

Revision ID: 7941988f444a
Revises: e39fd2ea2f5f
Create Date: 2025-11-21 20:06:06.762394

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '7941988f444a'
down_revision = 'e39fd2ea2f5f'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(255),
        phone VARCHAR(50),
        user_type user_role_type NOT NULL DEFAULT 'customer',
        is_active BOOLEAN DEFAULT TRUE,
        last_login_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # Create trigger for updated_at
    op.execute("""
    CREATE TRIGGER update_users_modtime
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
    """)


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS update_users_modtime ON users")
    op.execute("DROP TABLE IF EXISTS users")
