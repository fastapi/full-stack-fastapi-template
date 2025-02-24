"""add fulltext index for patient.medical_history

Revision ID: 60300545fecf
Revises: 9e47d43a4b8a
Create Date: 2025-02-23 19:56:05.494933

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '60300545fecf'
down_revision = '9e47d43a4b8a'
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
