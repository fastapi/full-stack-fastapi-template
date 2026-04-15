"""Add notification table

Revision ID: add_notification_table
Revises: 1a31ce608336
Create Date: 2026-04-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'add_notification_table'
down_revision = '1a31ce608336'
branch_labels = None
depends_on = None


def upgrade():
    # Create notification table
    op.create_table(
        'notification',
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('message', sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True),
        sa.Column('notification_type', sa.Enum('INFO', 'SUCCESS', 'WARNING', 'ERROR', name='notificationtype'), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column('action_url', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    # Create index on user_id for faster queries
    op.create_index(op.f('ix_notification_user_id'), 'notification', ['user_id'], unique=False)
    # Create index on created_at for ordering
    op.create_index(op.f('ix_notification_created_at'), 'notification', ['created_at'], unique=False)
    # Create index on is_read for filtering
    op.create_index(op.f('ix_notification_is_read'), 'notification', ['is_read'], unique=False)


def downgrade():
    # Drop indexes first
    op.drop_index(op.f('ix_notification_is_read'), table_name='notification')
    op.drop_index(op.f('ix_notification_created_at'), table_name='notification')
    op.drop_index(op.f('ix_notification_user_id'), table_name='notification')
    # Drop table
    op.drop_table('notification')
    # Drop enum type
    op.execute('DROP TYPE IF EXISTS notificationtype')
