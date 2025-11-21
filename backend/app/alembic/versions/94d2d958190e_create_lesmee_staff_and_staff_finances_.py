"""Create LESMEE Staff and Staff_Finances tables

Revision ID: 94d2d958190e
Revises: 7941988f444a
Create Date: 2025-11-21 20:06:21.436135

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '94d2d958190e'
down_revision = '7941988f444a'
branch_labels = None
depends_on = None


def upgrade():
    # Staff table
    op.execute("""
    CREATE TABLE staff (
        id SERIAL PRIMARY KEY,
        user_id INT UNIQUE NOT NULL REFERENCES users(id),
        employee_code VARCHAR(50) UNIQUE,
        role staff_role_type NOT NULL,
        department VARCHAR(100),
        skill_level INT DEFAULT 1,
        is_available BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # Staff finances table
    op.execute("""
    CREATE TABLE staff_finances (
        staff_id INT PRIMARY KEY REFERENCES staff(id),
        base_salary NUMERIC(19, 4) DEFAULT 0,
        bank_name VARCHAR(255),
        bank_account VARCHAR(50),
        tax_code VARCHAR(50),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # Create trigger for staff table
    op.execute("CREATE TRIGGER update_staff_modtime BEFORE UPDATE ON staff FOR EACH ROW EXECUTE PROCEDURE update_modified_column();")


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS update_staff_modtime ON staff")
    op.execute("DROP TABLE IF EXISTS staff_finances")
    op.execute("DROP TABLE IF EXISTS staff")
