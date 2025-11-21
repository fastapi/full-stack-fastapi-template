"""Create LESMEE ENUM types

Revision ID: e7864355f3d1
Revises: 61e21c4d3142
Create Date: 2025-11-21 20:03:41.589676

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'e7864355f3d1'
down_revision = '61e21c4d3142'
branch_labels = None
depends_on = None


def upgrade():
    # User and Staff Role ENUMs
    op.execute("CREATE TYPE user_role_type AS ENUM ('customer', 'staff', 'admin')")
    op.execute("CREATE TYPE staff_role_type AS ENUM ('editor', 'qa', 'saler', 'director', 'manager', 'admin')")

    # Order and Item Status ENUMs
    op.execute("CREATE TYPE order_status_type AS ENUM ('new', 'assigned', 'in_progress', 'review', 'completed', 'cancelled')")
    op.execute("CREATE TYPE item_status_type AS ENUM ('pending', 'assigned', 'in_progress', 'completed', 'rejected')")

    # Workflow ENUMs
    op.execute("CREATE TYPE work_type_enum AS ENUM ('editing', 'qa', 'review', 'correction')")
    op.execute("CREATE TYPE work_status_type AS ENUM ('assigned', 'accepted', 'in_progress', 'completed', 'rejected')")

    # Financial ENUMs
    op.execute("CREATE TYPE invoice_status_type AS ENUM ('draft', 'sent', 'paid', 'overdue', 'cancelled')")
    op.execute("CREATE TYPE commission_type_enum AS ENUM ('saler_bonus', 'director_fee', 'editor_payment', 'qa_fee')")

    # Issue Management ENUMs
    op.execute("CREATE TYPE issue_severity_type AS ENUM ('low', 'medium', 'high', 'critical')")
    op.execute("CREATE TYPE issue_status_type AS ENUM ('open', 'in_progress', 'resolved', 'closed')")

    # File Management ENUMs
    op.execute("CREATE TYPE file_type_enum AS ENUM ('customer_input', 'deliverable', 'reference')")


def downgrade():
    # Drop ENUMs in reverse order of creation
    op.execute("DROP TYPE IF EXISTS file_type_enum")
    op.execute("DROP TYPE IF EXISTS issue_status_type")
    op.execute("DROP TYPE IF EXISTS issue_severity_type")
    op.execute("DROP TYPE IF EXISTS commission_type_enum")
    op.execute("DROP TYPE IF EXISTS invoice_status_type")
    op.execute("DROP TYPE IF EXISTS work_status_type")
    op.execute("DROP TYPE IF EXISTS work_type_enum")
    op.execute("DROP TYPE IF EXISTS item_status_type")
    op.execute("DROP TYPE IF EXISTS order_status_type")
    op.execute("DROP TYPE IF EXISTS staff_role_type")
    op.execute("DROP TYPE IF EXISTS user_role_type")
