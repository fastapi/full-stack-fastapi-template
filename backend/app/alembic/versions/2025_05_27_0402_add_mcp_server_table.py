"""Add MCP server table

Revision ID: 2025_05_27_0402
Revises: 2025_05_26_1343
Create Date: 2025-05-27 04:02:50.892296

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '2025_05_27_0402'
down_revision: Union[str, None] = '2025_05_26_1343'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type for transport
    op.execute("CREATE TYPE mcptransporttype AS ENUM ('stdio', 'http_sse')")
    
    # Create mcp_servers table
    op.create_table('mcp_servers',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('transport', sa.Enum('stdio', 'http_sse', name='mcptransporttype'), nullable=False),
        sa.Column('command', sa.String(), nullable=True),
        sa.Column('args', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('headers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_remote', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('capabilities', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('tools', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('resources', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('prompts', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mcp_servers_id'), 'mcp_servers', ['id'], unique=False)
    op.create_index(op.f('ix_mcp_servers_name'), 'mcp_servers', ['name'], unique=True)


def downgrade() -> None:
    # Drop table and indexes
    op.drop_index(op.f('ix_mcp_servers_name'), table_name='mcp_servers')
    op.drop_index(op.f('ix_mcp_servers_id'), table_name='mcp_servers')
    op.drop_table('mcp_servers')
    
    # Drop enum type
    op.execute("DROP TYPE mcptransporttype")