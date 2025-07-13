"""add_ai_soul_entity_models

Revision ID: add_ai_soul_entity_models
Revises: add_timestamps_to_user
Create Date: 2024-03-24 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql
from datetime import datetime
import uuid
import bcrypt


# revision identifiers, used by Alembic.
revision: str = 'add_ai_soul_entity_models'
down_revision: Union[str, None] = 'add_timestamps_to_user'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create AI Soul Entity table
    op.create_table(
        'aisoulentity',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('persona_type', sa.String(length=50), nullable=False),
        sa.Column('specializations', sa.String(length=500), nullable=False),
        sa.Column('base_prompt', sa.String(length=5000), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('interaction_count', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create default AI Soul for existing chat messages
    default_user_id = uuid.uuid4()
    hashed_password = bcrypt.hashpw('password'.encode(), bcrypt.gensalt()).decode()
    
    # Create default user if not exists
    op.execute(f"""
        INSERT INTO "user" (
            id, email, hashed_password, is_active, is_superuser, created_at, updated_at
        ) VALUES (
            '{default_user_id}',
            'admin@example.com',
            '{hashed_password}',
            true,
            true,
            NOW(),
            NOW()
        )
        ON CONFLICT (email) DO NOTHING
    """)
    
    # Get the user ID (either the one we just created or the existing one)
    op.execute("""
        INSERT INTO aisoulentity (
            id, name, description, persona_type, specializations, base_prompt,
            is_active, user_id, created_at, updated_at, interaction_count
        ) VALUES (
            '00000000-0000-0000-0000-000000000000',
            'Default AI Soul',
            'Default AI Soul for existing chat messages',
            'default',
            'general',
            'You are a helpful AI assistant.',
            true,
            (SELECT id FROM "user" WHERE email = 'admin@example.com' LIMIT 1),
            NOW(),
            NOW(),
            0
        )
    """)


def downgrade() -> None:
    # Drop AI Soul Entity table
    op.drop_table('aisoulentity') 