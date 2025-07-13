"""edit_replace_id_integers_in_all_models

Revision ID: d98dd8ec85a3
Revises: add_uuid_extension
Create Date: 2024-03-24 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd98dd8ec85a3'
down_revision: Union[str, None] = 'add_uuid_extension'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Temporarily drop foreign key constraints
    op.drop_constraint('item_owner_id_fkey', 'item', type_='foreignkey')
    
    # Alter user table
    op.alter_column('user', 'id',
        type_=postgresql.UUID(),
        postgresql_using='uuid_generate_v4()',
        existing_type=sa.Integer(),
        nullable=False)
    
    # Alter item table
    op.alter_column('item', 'id',
        type_=postgresql.UUID(),
        postgresql_using='uuid_generate_v4()',
        existing_type=sa.Integer(),
        nullable=False)
    op.alter_column('item', 'owner_id',
        type_=postgresql.UUID(),
        postgresql_using='uuid_generate_v4()',
        existing_type=sa.Integer(),
        nullable=False)
    
    # Recreate foreign key constraints with UUID types
    op.create_foreign_key(
        'item_owner_id_fkey',
        'item', 'user',
        ['owner_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # This is a one-way migration - downgrade would lose data
    raise Exception("Downgrade not supported for UUID conversion")
