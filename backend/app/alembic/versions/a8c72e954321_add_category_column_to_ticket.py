"""
Add category column to ticket

Revision ID: a8c72e954321
Revises: f23a9c45d178
Create Date: 2023-11-15 14:30:00.000000
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = 'a8c72e954321'
down_revision = 'f23a9c45d178'
branch_labels = None
depends_on = None


def upgrade():
    # Add category column to ticket table with default value for existing records
    op.add_column('ticket', sa.Column('category', sqlmodel.sql.sqltypes.AutoString(), 
                                      nullable=False, 
                                      server_default='Suporte'))


def downgrade():
    # Remove category column from ticket table
    op.drop_column('ticket', 'category')
