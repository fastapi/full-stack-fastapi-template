"""Create LESMEE Settings and Audit Logs tables

Revision ID: 1888a26586e5
Revises: afa0d7780e75
Create Date: 2025-11-21 20:15:15.383638

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '1888a26586e5'
down_revision = 'afa0d7780e75'
branch_labels = None
depends_on = None


def upgrade():
    # Settings table
    op.execute("""
    CREATE TABLE settings (
        key VARCHAR(100) PRIMARY KEY,
        value TEXT,
        description TEXT,
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # Audit logs table
    op.execute("""
    CREATE TABLE audit_logs (
        id SERIAL PRIMARY KEY,
        user_id INT REFERENCES users(id),
        action_type VARCHAR(50) NOT NULL,
        table_name VARCHAR(100),
        record_id VARCHAR(50),
        old_values JSONB,
        new_values JSONB,
        ip_address VARCHAR(45),
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # Create indexes for audit logs
    op.execute("CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);")
    op.execute("CREATE INDEX idx_audit_logs_user_action ON audit_logs(user_id, action_type);")
    op.execute("CREATE INDEX idx_audit_logs_table_name ON audit_logs(table_name);")

    # Additional performance indexes
    op.execute("CREATE INDEX idx_orders_status_deadline ON orders(status, deadline_at);")
    op.execute("CREATE INDEX idx_orders_customer_product ON orders(customer_id, product_id);")
    op.execute("CREATE INDEX idx_orders_created_at ON orders(ordered_at DESC);")
    op.execute("CREATE INDEX idx_order_items_status ON order_items(status);")
    op.execute("CREATE INDEX idx_order_items_staff ON order_items(assigned_staff_id);")
    op.execute("CREATE INDEX idx_work_assignments_type_status ON work_assignments(work_type, status);")
    op.execute("CREATE INDEX idx_work_assignments_assigned_at ON work_assignments(assigned_at DESC);")
    op.execute("CREATE INDEX idx_work_assignments_completion ON work_assignments(completed_at);")
    op.execute("CREATE INDEX idx_commissions_staff_type ON commissions(staff_id, commission_type);")
    op.execute("CREATE INDEX idx_commissions_paid_status ON commissions(is_paid);")
    op.execute("CREATE INDEX idx_staff_department ON staff(department);")
    op.execute("CREATE INDEX idx_customers_vip_status ON customers(is_vip);")


def downgrade():
    # Drop additional performance indexes
    op.execute("DROP INDEX IF EXISTS idx_customers_vip_status")
    op.execute("DROP INDEX IF EXISTS idx_staff_department")
    op.execute("DROP INDEX IF EXISTS idx_commissions_paid_status")
    op.execute("DROP INDEX IF EXISTS idx_commissions_staff_type")
    op.execute("DROP INDEX IF EXISTS idx_work_assignments_completion")
    op.execute("DROP INDEX IF EXISTS idx_work_assignments_assigned_at")
    op.execute("DROP INDEX IF EXISTS idx_work_assignments_type_status")
    op.execute("DROP INDEX IF EXISTS idx_order_items_staff")
    op.execute("DROP INDEX IF EXISTS idx_order_items_status")
    op.execute("DROP INDEX IF EXISTS idx_orders_created_at")
    op.execute("DROP INDEX IF EXISTS idx_orders_customer_product")
    op.execute("DROP INDEX IF EXISTS idx_orders_status_deadline")

    # Drop audit log indexes
    op.execute("DROP INDEX IF EXISTS idx_audit_logs_table_name")
    op.execute("DROP INDEX IF EXISTS idx_audit_logs_user_action")
    op.execute("DROP INDEX IF EXISTS idx_audit_logs_created_at")

    # Drop tables
    op.execute("DROP TABLE IF EXISTS audit_logs")
    op.execute("DROP TABLE IF EXISTS settings")
