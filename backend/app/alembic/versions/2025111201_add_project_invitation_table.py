"""add project invitation table

Revision ID: 2025111201
Revises: 2025110302
Create Date: 2025-11-12

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2025111201'
down_revision = '2025110302'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'projectinvitation',
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('role', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('can_comment', sa.Boolean(), nullable=False),
        sa.Column('can_download', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('project_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projectinvitation_email'), 'projectinvitation', ['email'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_projectinvitation_email'), table_name='projectinvitation')
    op.drop_table('projectinvitation')

