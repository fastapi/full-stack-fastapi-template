"""Add extractions table with enum, indexes, and trigger

Revision ID: 460746be37d1
Revises: 1a31ce608336
Create Date: 2025-10-25 18:51:21.845738

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '460746be37d1'
down_revision = '1a31ce608336'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create PostgreSQL enum type for extraction status (using IF NOT EXISTS for safety)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE extraction_status AS ENUM (
                'UPLOADED',
                'OCR_PROCESSING',
                'OCR_COMPLETE',
                'SEGMENTATION_PROCESSING',
                'SEGMENTATION_COMPLETE',
                'TAGGING_PROCESSING',
                'DRAFT',
                'IN_REVIEW',
                'APPROVED',
                'REJECTED',
                'FAILED'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # 2. Create extractions table
    # Note: Using postgresql.ENUM to reference the already-created type
    from sqlalchemy.dialects import postgresql
    op.create_table(
        'extractions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.Column('filename', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('mime_type', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('status', postgresql.ENUM(
            'UPLOADED', 'OCR_PROCESSING', 'OCR_COMPLETE',
            'SEGMENTATION_PROCESSING', 'SEGMENTATION_COMPLETE',
            'TAGGING_PROCESSING', 'DRAFT', 'IN_REVIEW',
            'APPROVED', 'REJECTED', 'FAILED',
            name='extraction_status',
            create_type=False  # Don't create the type, we already did it above
        ), nullable=False, server_default='UPLOADED'),
        sa.Column('presigned_url', sqlmodel.sql.sqltypes.AutoString(length=2048), nullable=False),
        sa.Column('storage_path', sqlmodel.sql.sqltypes.AutoString(length=512), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ondelete='CASCADE')
    )

    # 3. Create indexes for performance
    op.create_index('ix_extractions_owner_id', 'extractions', ['owner_id'])
    op.create_index('ix_extractions_status', 'extractions', ['status'])
    op.create_index('ix_extractions_uploaded_at', 'extractions', ['uploaded_at'])

    # 4. Add check constraint for file_size > 0
    op.create_check_constraint(
        'ck_extractions_file_size_positive',
        'extractions',
        'file_size > 0'
    )

    # 5. Create trigger function for auto-updating updated_at (idempotent)
    op.execute("""
        CREATE OR REPLACE FUNCTION trigger_set_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # 6. Attach trigger to extractions table
    op.execute("""
        CREATE TRIGGER set_timestamp
        BEFORE UPDATE ON extractions
        FOR EACH ROW
        EXECUTE FUNCTION trigger_set_timestamp();
    """)


def downgrade():
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS set_timestamp ON extractions")

    # Drop table (cascade will handle foreign keys)
    op.drop_table('extractions')

    # Drop enum type
    op.execute("DROP TYPE IF EXISTS extraction_status")

    # Note: Not dropping trigger_set_timestamp() function as other tables may use it
