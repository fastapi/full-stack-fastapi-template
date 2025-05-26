"""add_oauth_state_table_for_csrf_protection

Revision ID: 87ddaa4fab90
Revises: 1a31ce608336
Create Date: 2025-05-26 13:43:36.423557+00:00

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '87ddaa4fab90'
down_revision = '1a31ce608336'
branch_labels = None
depends_on = None


def upgrade():
    # Create oauth_state table
    op.create_table(
        'oauthstate',
        sa.Column('state_token', sa.String(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('redirect_uri', sa.String(length=500), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_oauthstate_state_token'), 'oauthstate', ['state_token'], unique=True)
    
    # Create index for cleanup queries
    op.create_index('ix_oauthstate_expires_at', 'oauthstate', ['expires_at'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_oauthstate_expires_at', table_name='oauthstate')
    op.drop_index(op.f('ix_oauthstate_state_token'), table_name='oauthstate')
    
    # Drop table
    op.drop_table('oauthstate')