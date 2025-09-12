"""add_wallet_and_transaction_models

Revision ID: fd8dcfe8d4fd
Revises: 1a31ce608336
Create Date: 2025-09-12 22:28:29.785616

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fd8dcfe8d4fd"
down_revision = "1a31ce608336"
branch_labels = None
depends_on = None


def upgrade():
    # Create wallet table
    op.create_table(
        "wallet",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "currency",
            sa.Enum("USD", "EUR", "RUB", name="currencyenum"),
            nullable=False,
        ),
        sa.Column("balance", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create transaction table
    op.create_table(
        "transaction",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("wallet_id", sa.UUID(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "type",
            sa.Enum("credit", "debit", name="transactiontypeenum"),
            nullable=False,
        ),
        sa.Column(
            "currency",
            sa.Enum("USD", "EUR", "RUB", name="currencyenum"),
            nullable=False,
        ),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallet.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    # Drop transaction table
    op.drop_table("transaction")

    # Drop wallet table
    op.drop_table("wallet")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS transactiontypeenum")
    op.execute("DROP TYPE IF EXISTS currencyenum")
