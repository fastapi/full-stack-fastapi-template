"""
Add category to ticket table
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'b54d6e812a9c'
down_revision = 'f23a9c45d178'
branch_labels = None
depends_on = None


def upgrade():
    # Add category column to ticket table
    op.add_column('ticket', sa.Column('category', sqlmodel.sql.sqltypes.AutoString(), nullable=False, 
                                     server_default="Suporte"))  # Default to "Suporte" for existing tickets


def downgrade():
    # Remove category column from ticket table
    op.drop_column('ticket', 'category')
