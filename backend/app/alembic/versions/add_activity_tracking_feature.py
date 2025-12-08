"""add activity tracking feature

Revision ID: f8e3d4c2a1b9
Revises: 1a31ce608336
Create Date: 2025-12-08 22:17:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f8e3d4c2a1b9'
down_revision = '1a31ce608336'
branch_labels = None
depends_on = None


def upgrade():
    # Add activity tracking columns to item table
    op.add_column('item', sa.Column('activity_score', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('item', sa.Column('last_accessed', sa.DateTime(), nullable=True))
    op.add_column('item', sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'))
    
    # Create itemactivity table
    op.create_table('itemactivity',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('activity_type', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('activity_metadata', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column('item_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['item_id'], ['item.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_itemactivity_item_id', 'itemactivity', ['item_id'])
    op.create_index('ix_itemactivity_user_id', 'itemactivity', ['user_id'])
    op.create_index('ix_itemactivity_timestamp', 'itemactivity', ['timestamp'])
    op.create_index('ix_item_activity_score', 'item', ['activity_score'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_item_activity_score', table_name='item')
    op.drop_index('ix_itemactivity_timestamp', table_name='itemactivity')
    op.drop_index('ix_itemactivity_user_id', table_name='itemactivity')
    op.drop_index('ix_itemactivity_item_id', table_name='itemactivity')
    
    # Drop itemactivity table
    op.drop_table('itemactivity')
    
    # Remove columns from item table
    op.drop_column('item', 'view_count')
    op.drop_column('item', 'last_accessed')
    op.drop_column('item', 'activity_score')
