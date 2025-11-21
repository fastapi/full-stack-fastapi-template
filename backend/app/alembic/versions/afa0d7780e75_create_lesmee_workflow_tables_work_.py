"""Create LESMEE Workflow tables (Work Assignments, Commissions, Work History, Issues)

Revision ID: afa0d7780e75
Revises: a1fd466d2512
Create Date: 2025-11-21 20:11:57.416541

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'afa0d7780e75'
down_revision = 'a1fd466d2512'
branch_labels = None
depends_on = None


def upgrade():
    # Work assignments table
    op.execute("""
    CREATE TABLE work_assignments (
        id SERIAL PRIMARY KEY,
        order_item_id INT NOT NULL REFERENCES order_items(id),
        assigned_to INT NOT NULL REFERENCES staff(id),
        assigned_by INT NOT NULL REFERENCES users(id),
        work_type work_type_enum NOT NULL,
        status work_status_type DEFAULT 'assigned',
        assigned_at TIMESTAMPTZ DEFAULT NOW(),
        started_at TIMESTAMPTZ,
        completed_at TIMESTAMPTZ,
        estimated_hours INT,
        actual_hours NUMERIC(5, 2),
        staff_note TEXT,
        manager_note TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # Commissions table
    op.execute("""
    CREATE TABLE commissions (
        id SERIAL PRIMARY KEY,
        order_id UUID NOT NULL REFERENCES orders(id),
        staff_id INT NOT NULL REFERENCES staff(id),
        commission_type commission_type_enum NOT NULL,
        amount NUMERIC(19, 4) NOT NULL,
        percentage NUMERIC(5, 2),
        is_paid BOOLEAN DEFAULT FALSE,
        paid_date TIMESTAMPTZ,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # Work history table
    op.execute("""
    CREATE TABLE work_history (
        id SERIAL PRIMARY KEY,
        assignment_id INT REFERENCES work_assignments(id),
        work_item_id INT REFERENCES order_items(id),
        action_type VARCHAR(50) NOT NULL,
        action_by INT NOT NULL REFERENCES users(id),
        description TEXT,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # Issues table
    op.execute("""
    CREATE TABLE issues (
        id SERIAL PRIMARY KEY,
        order_item_id INT NOT NULL REFERENCES order_items(id),
        reported_by INT NOT NULL REFERENCES users(id),
        assigned_to INT REFERENCES staff(id),
        issue_type VARCHAR(50),
        severity issue_severity_type DEFAULT 'medium',
        status issue_status_type DEFAULT 'open',
        description TEXT NOT NULL,
        evidence_urls JSONB,
        resolution_note TEXT,
        resolved_by INT REFERENCES staff(id),
        resolved_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # Create triggers and indexes
    op.execute("CREATE TRIGGER update_work_assignments_modtime BEFORE UPDATE ON work_assignments FOR EACH ROW EXECUTE PROCEDURE update_modified_column();")
    op.execute("CREATE TRIGGER update_issues_modtime BEFORE UPDATE ON issues FOR EACH ROW EXECUTE PROCEDURE update_modified_column();")

    op.execute("CREATE INDEX idx_work_assignments_item ON work_assignments(order_item_id);")
    op.execute("CREATE INDEX idx_work_assignments_staff ON work_assignments(assigned_to);")
    op.execute("CREATE INDEX idx_work_assignments_status ON work_assignments(status);")
    op.execute("CREATE INDEX idx_commissions_order_id ON commissions(order_id);")
    op.execute("CREATE INDEX idx_commissions_staff_id ON commissions(staff_id);")
    op.execute("CREATE INDEX idx_issues_order_item ON issues(order_item_id);")
    op.execute("CREATE INDEX idx_issues_status ON issues(status);")


def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_issues_status")
    op.execute("DROP INDEX IF EXISTS idx_issues_order_item")
    op.execute("DROP INDEX IF EXISTS idx_commissions_staff_id")
    op.execute("DROP INDEX IF EXISTS idx_commissions_order_id")
    op.execute("DROP INDEX IF EXISTS idx_work_assignments_status")
    op.execute("DROP INDEX IF EXISTS idx_work_assignments_staff")
    op.execute("DROP INDEX IF EXISTS idx_work_assignments_item")
    op.execute("DROP TRIGGER IF EXISTS update_issues_modtime ON issues")
    op.execute("DROP TRIGGER IF EXISTS update_work_assignments_modtime ON work_assignments")
    op.execute("DROP TABLE IF EXISTS issues")
    op.execute("DROP TABLE IF EXISTS work_history")
    op.execute("DROP TABLE IF EXISTS commissions")
    op.execute("DROP TABLE IF EXISTS work_assignments")
