"""Create LESMEE Invoices table for financial management

Revision ID: a1fd466d2512
Revises: cf2ea22e8259
Create Date: 2025-11-21 20:11:37.396093

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'a1fd466d2512'
down_revision = 'cf2ea22e8259'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE TABLE invoices (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        order_id UUID NOT NULL REFERENCES orders(id),
        invoice_number VARCHAR(50) UNIQUE,
        amount NUMERIC(19, 4) NOT NULL,
        status invoice_status_type DEFAULT 'draft',
        issue_date TIMESTAMPTZ DEFAULT NOW(),
        due_date TIMESTAMPTZ,
        paid_date TIMESTAMPTZ,
        commission_snapshot JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # Create trigger and indexes
    op.execute("CREATE TRIGGER update_invoices_modtime BEFORE UPDATE ON invoices FOR EACH ROW EXECUTE PROCEDURE update_modified_column();")
    op.execute("CREATE INDEX idx_invoices_order_id ON invoices(order_id);")
    op.execute("CREATE INDEX idx_invoices_status ON invoices(status);")


def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_invoices_status")
    op.execute("DROP INDEX IF EXISTS idx_invoices_order_id")
    op.execute("DROP TRIGGER IF EXISTS update_invoices_modtime ON invoices")
    op.execute("DROP TABLE IF EXISTS invoices")
