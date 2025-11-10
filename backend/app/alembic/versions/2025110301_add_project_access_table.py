"""Add project_access table for client invitations

Revision ID: 2025110301
Revises: 2025110201
Create Date: 2025-11-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2025110301'
down_revision = '2025110201'
branch_labels = None
depends_on = None


def upgrade():
    # Create project_access table
    op.create_table(
        'projectaccess',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('role', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False, server_default='viewer'),
        sa.Column('can_comment', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('can_download', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index for faster lookups
    op.create_index('ix_projectaccess_project_id', 'projectaccess', ['project_id'])
    op.create_index('ix_projectaccess_user_id', 'projectaccess', ['user_id'])
    
    # Create unique constraint to prevent duplicate access entries
    op.create_unique_constraint('uq_projectaccess_project_user', 'projectaccess', ['project_id', 'user_id'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_projectaccess_user_id', 'projectaccess')
    op.drop_index('ix_projectaccess_project_id', 'projectaccess')
    
    # Drop table
    op.drop_table('projectaccess')

