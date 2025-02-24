"""Add GIN index on patient medical_history

Revision ID: 2025_02_23_gin_idx
Revises: 
Create Date: 2025-02-23 10:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '2025_02_23_gin_idx'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create GIN index on medical_history column
    op.execute("""
        CREATE EXTENSION IF NOT EXISTS pg_trgm;
        CREATE INDEX IF NOT EXISTS ix_patient_medical_history_gin 
        ON patient 
        USING GIN (medical_history gin_trgm_ops);
    """)


def downgrade() -> None:
    # Drop the GIN index
    op.execute("""
        DROP INDEX IF EXISTS ix_patient_medical_history_gin;
    """)
