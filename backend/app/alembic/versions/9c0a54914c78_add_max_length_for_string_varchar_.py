"""Add max length for string(varchar) fields in User and Items models.

Revision ID: 9c0a54914c78
Revises: e2412789c190
Create Date: 2024-06-17 14:42:44.639457

"""

import sqlalchemy as sa
from alembic import op

# Constants
STRING_FIELD_LENGTH = 255
USER_TABLE = "user"
ITEM_TABLE = "item"

# revision identifiers, used by Alembic.
revision = "9c0a54914c78"
down_revision = "e2412789c190"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Adjust the length of the email field in the User table
    op.alter_column(
        USER_TABLE,
        "email",
        existing_type=sa.String(),
        type_=sa.String(length=STRING_FIELD_LENGTH),
        existing_nullable=False,
    )

    # Adjust the length of the full_name field in the User table
    op.alter_column(
        USER_TABLE,
        "full_name",
        existing_type=sa.String(),
        type_=sa.String(length=STRING_FIELD_LENGTH),
        existing_nullable=True,
    )

    # Adjust the length of the title field in the Item table
    op.alter_column(
        ITEM_TABLE,
        "title",
        existing_type=sa.String(),
        type_=sa.String(length=STRING_FIELD_LENGTH),
        existing_nullable=False,
    )

    # Adjust the length of the description field in the Item table
    op.alter_column(
        ITEM_TABLE,
        "description",
        existing_type=sa.String(),
        type_=sa.String(length=STRING_FIELD_LENGTH),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade database schema."""
    # Revert the length of the email field in the User table
    op.alter_column(
        USER_TABLE,
        "email",
        existing_type=sa.String(length=STRING_FIELD_LENGTH),
        type_=sa.String(),
        existing_nullable=False,
    )

    # Revert the length of the full_name field in the User table
    op.alter_column(
        USER_TABLE,
        "full_name",
        existing_type=sa.String(length=STRING_FIELD_LENGTH),
        type_=sa.String(),
        existing_nullable=True,
    )

    # Revert the length of the title field in the Item table
    op.alter_column(
        ITEM_TABLE,
        "title",
        existing_type=sa.String(length=STRING_FIELD_LENGTH),
        type_=sa.String(),
        existing_nullable=False,
    )

    # Revert the length of the description field in the Item table
    op.alter_column(
        ITEM_TABLE,
        "description",
        existing_type=sa.String(length=STRING_FIELD_LENGTH),
        type_=sa.String(),
        existing_nullable=True,
    )
