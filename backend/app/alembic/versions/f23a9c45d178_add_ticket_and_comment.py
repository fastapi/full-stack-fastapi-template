"""
Add ticket and comment tables
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4


# revision identifiers, used by Alembic.
revision = 'f23a9c45d178'
down_revision = '1a31ce608336'
branch_labels = None
depends_on = None


def upgrade():
    # Create ticket table
    op.create_table(
        'ticket',
        sa.Column("id", UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("priority", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("user_id", UUID(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], ondelete="CASCADE"
        ),
    )
    
    # Create index for ticket lookup by owner
    op.create_index(op.f('ix_ticket_owner_id'), 'ticket', ['owner_id'], unique=False)
    
    # Create comment table
    op.create_table(
        'comment',
        sa.Column("id", UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("content", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("ticket_id", UUID(), nullable=False),
        sa.Column("user_id", UUID(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["ticket_id"], ["ticket.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], ondelete="CASCADE"
        ),
    )
    
    # Create indexes for faster comment lookups
    op.create_index(op.f('ix_comment_ticket_id'), 'comment', ['ticket_id'], unique=False)
    op.create_index(op.f('ix_comment_user_id'), 'comment', ['user_id'], unique=False)


def downgrade():
    # Drop tables in reverse order (comments first, then tickets)
    op.drop_index(op.f('ix_comment_user_id'), table_name='comment')
    op.drop_index(op.f('ix_comment_ticket_id'), table_name='comment')
    op.drop_table('comment')
    
    op.drop_index(op.f('ix_ticket_owner_id'), table_name='ticket')
    op.drop_table('ticket')
