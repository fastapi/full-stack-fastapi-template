"""add_multi_language_support

Revision ID: 88968afdc9ad
Revises: 064eff5bcff1
Create Date: 2026-05-16 23:18:20.192695

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = '88968afdc9ad'
down_revision = '064eff5bcff1'
branch_labels = None
depends_on = None


def upgrade():
    # Add translations column to race table
    # Stores translations as JSON: {"vi": {"name": "...", "description": "..."}, "en": {...}}
    op.add_column('race', sa.Column('translations', JSON, nullable=True))
    
    # Add translations column to racecategory table
    # Stores translations as JSON: {"vi": {"name": "...", "description": "..."}, "en": {...}}
    op.add_column('racecategory', sa.Column('translations', JSON, nullable=True))
    
    # Add translations column to racetag table
    # Stores translations as JSON: {"vi": {"name": "..."}, "en": {...}}
    op.add_column('racetag', sa.Column('translations', JSON, nullable=True))
    
    # Add default_language column to race table
    op.add_column('race', sa.Column('default_language', sa.String(length=10), nullable=False, server_default='en'))


def downgrade():
    op.drop_column('race', 'default_language')
    op.drop_column('racetag', 'translations')
    op.drop_column('racecategory', 'translations')
    op.drop_column('race', 'translations')

