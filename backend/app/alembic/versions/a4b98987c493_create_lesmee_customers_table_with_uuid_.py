"""Create LESMEE Customers table with UUID primary key

Revision ID: a4b98987c493
Revises: 94d2d958190e
Create Date: 2025-11-21 20:06:34.960350

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'a4b98987c493'
down_revision = '94d2d958190e'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE TABLE customers (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id INT UNIQUE NOT NULL REFERENCES users(id),
        customer_code VARCHAR(50) UNIQUE,
        company_name VARCHAR(255),
        address TEXT,
        is_vip BOOLEAN DEFAULT FALSE,
        sales_rep_id INT REFERENCES staff(id),
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # Create trigger
    op.execute("CREATE TRIGGER update_customers_modtime BEFORE UPDATE ON customers FOR EACH ROW EXECUTE PROCEDURE update_modified_column();")

    # Create indexes
    op.execute("CREATE INDEX idx_customers_user_id ON customers(user_id);")
    op.execute("CREATE INDEX idx_customers_sales_rep ON customers(sales_rep_id);")


def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_customers_sales_rep")
    op.execute("DROP INDEX IF EXISTS idx_customers_user_id")
    op.execute("DROP TRIGGER IF EXISTS update_customers_modtime ON customers")
    op.execute("DROP TABLE IF EXISTS customers")
