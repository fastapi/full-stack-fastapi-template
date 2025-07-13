"""remove_sharing_tables

Revision ID: 002_remove_sharing_tables
Revises: 8cf5c34c4462
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_remove_sharing_tables'
down_revision = '8cf5c34c4462'
branch_labels = None
depends_on = None


def upgrade():
    # Drop sharing-related tables
    op.drop_table('sharedchatmessage')
    op.drop_table('sharedchatsession')
    op.drop_table('aisoulentityshare')


def downgrade():
    # Recreate sharing tables
    op.create_table(
        'aisoulentityshare',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('allow_anonymous', sa.Boolean(), nullable=False),
        sa.Column('share_code', sa.String(length=50), nullable=False),
        sa.Column('owner_id', postgresql.UUID(), nullable=False),
        sa.Column('ai_soul_id', postgresql.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('access_count', sa.Integer(), nullable=False),
        sa.Column('last_accessed', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ai_soul_id'], ['aisoulentity.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('share_code')
    )

    op.create_table(
        'sharedchatsession',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('session_name', sa.String(length=255), nullable=True),
        sa.Column('share_id', postgresql.UUID(), nullable=False),
        sa.Column('visitor_identifier', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_message_at', sa.DateTime(), nullable=False),
        sa.Column('message_count', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['share_id'], ['aisoulentityshare.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'sharedchatmessage',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('session_id', postgresql.UUID(), nullable=False),
        sa.Column('content', sa.String(length=5000), nullable=False),
        sa.Column('is_from_visitor', sa.Boolean(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sharedchatsession.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    ) 