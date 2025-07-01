"""add clerk_id to users

Revision ID: clerk_user_update
Revises: railway_complete_migration
Create Date: 2024-12-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'clerk_user_update'
down_revision = 'railway_complete_migration'
branch_labels = None
depends_on = None


def upgrade():
    # Agregar campo clerk_id a la tabla user
    op.add_column('user', sa.Column('clerk_id', sa.String(), nullable=True))
    
    # Crear índice único para clerk_id
    op.create_index('ix_user_clerk_id', 'user', ['clerk_id'], unique=True)
    
    # Hacer que hashed_password sea opcional (default empty string)
    op.alter_column('user', 'hashed_password',
                    existing_type=sa.VARCHAR(),
                    nullable=False,
                    server_default=sa.text("''"))


def downgrade():
    # Eliminar índice y columna
    op.drop_index('ix_user_clerk_id', table_name='user')
    op.drop_column('user', 'clerk_id')
    
    # Revertir hashed_password
    op.alter_column('user', 'hashed_password',
                    existing_type=sa.VARCHAR(),
                    nullable=False,
                    server_default=None) 