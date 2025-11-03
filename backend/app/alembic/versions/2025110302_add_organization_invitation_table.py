"""add organization invitation table

Revision ID: 2025110302
Revises: 2025110301
Create Date: 2025-11-03

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2025110302'
down_revision = '2025110301'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'organizationinvitation',
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizationinvitation_email'), 'organizationinvitation', ['email'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_organizationinvitation_email'), table_name='organizationinvitation')
    op.drop_table('organizationinvitation')

