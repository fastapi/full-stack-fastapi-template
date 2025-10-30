"""initial_schema

This migration represents the baseline database schema as of 2025-10-30.

The database already contains the following tables:
- user: Core user authentication table with RLS enabled
- ingestions: PDF ingestion tracking with OCR metadata fields
- alembic_version: Migration tracking

This is a marker migration created after resetting the migration history.
No actual schema changes are performed - the database already has these tables.

All previous migration history was reset to start fresh in early development.
Future migrations will build on top of this baseline.

Revision ID: 20038a3ab258
Revises:
Create Date: 2025-10-30 15:35:13.282800

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '20038a3ab258'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Baseline migration - no operations needed.

    The database already contains:
    - user table (6 columns, RLS enabled)
    - ingestions table (16 columns including OCR fields, RLS enabled)
    """
    pass


def downgrade():
    """Cannot downgrade from baseline migration.

    This represents the initial state - there is nothing to downgrade to.
    """
    pass
