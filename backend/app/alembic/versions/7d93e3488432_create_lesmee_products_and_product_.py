"""Create LESMEE Products and Product Options tables

Revision ID: 7d93e3488432
Revises: 03422fadcc73
Create Date: 2025-11-21 20:11:01.140758

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '7d93e3488432'
down_revision = '03422fadcc73'
branch_labels = None
depends_on = None


def upgrade():
    # Products table
    op.execute("""
    CREATE TABLE products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        slug VARCHAR(255) UNIQUE,
        base_price NUMERIC(19, 4) NOT NULL DEFAULT 0,
        category VARCHAR(100),
        description TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        commission_config JSONB DEFAULT '{}',
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # Product options table
    op.execute("""
    CREATE TABLE product_options (
        id SERIAL PRIMARY KEY,
        product_id INT NOT NULL REFERENCES products(id),
        option_name VARCHAR(255) NOT NULL,
        is_required BOOLEAN DEFAULT FALSE,
        price_adjustment NUMERIC(19, 4) DEFAULT 0,
        option_values JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # Create trigger
    op.execute("CREATE TRIGGER update_products_modtime BEFORE UPDATE ON products FOR EACH ROW EXECUTE PROCEDURE update_modified_column();")

    # Create indexes
    op.execute("CREATE INDEX idx_products_category ON products(category);")
    op.execute("CREATE INDEX idx_products_is_active ON products(is_active);")
    op.execute("CREATE INDEX idx_product_options_product_id ON product_options(product_id);")


def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_product_options_product_id")
    op.execute("DROP INDEX IF EXISTS idx_products_is_active")
    op.execute("DROP INDEX IF EXISTS idx_products_category")
    op.execute("DROP TRIGGER IF EXISTS update_products_modtime ON products")
    op.execute("DROP TABLE IF EXISTS product_options")
    op.execute("DROP TABLE IF EXISTS products")
