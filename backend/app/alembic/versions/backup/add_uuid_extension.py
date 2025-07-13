"""add_uuid_extension

Revision ID: add_uuid_extension
Revises: e2412789c190
Create Date: 2024-03-24 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_uuid_extension'
down_revision: Union[str, None] = 'e2412789c190'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add uuid-ossp extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')


def downgrade() -> None:
    # Remove uuid-ossp extension
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"') 