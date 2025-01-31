"""add path and step models

Revision ID: ea8d60701d49
Revises: 1a31ce608336
Create Date: 2025-01-31 17:08:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'ea8d60701d49'
down_revision: Union[str, None] = '1a31ce608336'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create path table
    op.create_table(
        'path',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('creator_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('path_summary', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['creator_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create step table and sequence
    op.create_sequence('step_id_seq')
    op.create_table(
        'step',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('path_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('role_prompt', sa.String(), nullable=True),
        sa.Column('validation_prompt', sa.String(), nullable=True),
        sa.Column('exposition_json', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['path_id'], ['path.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('step')
    op.drop_sequence('step_id_seq')
    op.drop_table('path')
