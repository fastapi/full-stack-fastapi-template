"""Create LESMEE Orders, Order Items, and Order Attachments tables

Revision ID: cf2ea22e8259
Revises: 7d93e3488432
Create Date: 2025-11-21 20:11:16.572460

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'cf2ea22e8259'
down_revision = '7d93e3488432'
branch_labels = None
depends_on = None


def upgrade():
    # Orders table
    op.execute("""
    CREATE TABLE orders (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        order_number VARCHAR(50) UNIQUE NOT NULL,
        customer_id UUID NOT NULL REFERENCES customers(id),
        product_id INT NOT NULL REFERENCES products(id),
        parent_order_id UUID REFERENCES orders(id),
        status order_status_type DEFAULT 'new',
        total_amount NUMERIC(19, 4) NOT NULL DEFAULT 0,
        discount_amount NUMERIC(19, 4) DEFAULT 0,
        paid_amount NUMERIC(19, 4) DEFAULT 0,
        currency VARCHAR(3) DEFAULT 'USD',
        assigned_director_id INT REFERENCES staff(id),
        assigned_saler_id INT REFERENCES staff(id),
        ordered_at TIMESTAMPTZ DEFAULT NOW(),
        deadline_at TIMESTAMPTZ,
        completed_at TIMESTAMPTZ,
        customer_note TEXT,
        internal_note TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # Order items table
    op.execute("""
    CREATE TABLE order_items (
        id SERIAL PRIMARY KEY,
        order_id UUID NOT NULL REFERENCES orders(id),
        item_name VARCHAR(255) NOT NULL,
        quantity INT DEFAULT 1,
        unit_price NUMERIC(19, 4) NOT NULL,
        specifications JSONB DEFAULT '{}',
        assigned_staff_id INT REFERENCES staff(id),
        status item_status_type DEFAULT 'pending',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # Order attachments table
    op.execute("""
    CREATE TABLE order_attachments (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        order_id UUID NOT NULL REFERENCES orders(id),
        file_name VARCHAR(255) NOT NULL,
        file_path TEXT NOT NULL,
        file_type file_type_enum NOT NULL,
        uploaded_by INT NOT NULL REFERENCES users(id),
        uploaded_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # Create triggers
    op.execute("CREATE TRIGGER update_orders_modtime BEFORE UPDATE ON orders FOR EACH ROW EXECUTE PROCEDURE update_modified_column();")

    # Create indexes
    op.execute("CREATE INDEX idx_orders_customer_id ON orders(customer_id);")
    op.execute("CREATE INDEX idx_orders_parent_id ON orders(parent_order_id);")
    op.execute("CREATE INDEX idx_order_items_order_id ON order_items(order_id);")
    op.execute("CREATE INDEX idx_orders_status ON orders(status);")
    op.execute("CREATE INDEX idx_orders_order_number ON orders(order_number);")


def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_orders_order_number")
    op.execute("DROP INDEX IF EXISTS idx_orders_status")
    op.execute("DROP INDEX IF EXISTS idx_order_items_order_id")
    op.execute("DROP INDEX IF EXISTS idx_orders_parent_id")
    op.execute("DROP INDEX IF EXISTS idx_orders_customer_id")
    op.execute("DROP TRIGGER IF EXISTS update_orders_modtime ON orders")
    op.execute("DROP TABLE IF EXISTS order_attachments")
    op.execute("DROP TABLE IF EXISTS order_items")
    op.execute("DROP TABLE IF EXISTS orders")
