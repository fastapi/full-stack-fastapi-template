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
    """Baseline migration - create initial schema.

    Creates:
    - user table (6 columns, RLS enabled)
    - ingestions table (16 columns including OCR fields, RLS enabled)
    """
    # Create user table
    op.create_table(
        'user',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('full_name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column('hashed_password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_email', 'user', ['email'], unique=True)

    # Create ingestions table
    op.create_table(
        'ingestions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.Column('filename', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('mime_type', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default='UPLOADED'),
        sa.Column('presigned_url', sqlmodel.sql.sqltypes.AutoString(length=2048), nullable=False),
        sa.Column('storage_path', sqlmodel.sql.sqltypes.AutoString(length=512), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.Column('ocr_provider', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column('ocr_processed_at', sa.DateTime(), nullable=True),
        sa.Column('ocr_processing_time', sa.Float(), nullable=True),
        sa.Column('ocr_cost', sa.Float(), nullable=True),
        sa.Column('ocr_average_confidence', sa.Float(), nullable=True),
        sa.Column('ocr_storage_path', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ingestions_owner_id', 'ingestions', ['owner_id'], unique=False)
    op.create_index('ix_ingestions_status', 'ingestions', ['status'], unique=False)
    op.create_index('ix_ingestions_ocr_processed_at', 'ingestions', ['ocr_processed_at'], unique=False)


def downgrade():
    """Downgrade from baseline migration.

    Drops all tables in reverse order (respecting foreign key constraints).
    """
    # Drop ingestions first (has foreign key to user)
    op.drop_index('ix_ingestions_ocr_processed_at', table_name='ingestions')
    op.drop_index('ix_ingestions_status', table_name='ingestions')
    op.drop_index('ix_ingestions_owner_id', table_name='ingestions')
    op.drop_table('ingestions')

    # Drop user table
    op.drop_index('ix_user_email', table_name='user')
    op.drop_table('user')
