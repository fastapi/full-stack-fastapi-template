"""add article_like table

Revision ID: d4e5f6a7b8c9
Revises: c8d9e0f1a2b3
Create Date: 2026-07-02 00:00:00.000000

"""
from alembic import op

revision = "d4e5f6a7b8c9"
down_revision = "c8d9e0f1a2b3"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS article_like (
            user_id UUID NOT NULL REFERENCES "user" (id),
            article_id INTEGER NOT NULL REFERENCES article (id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY (user_id, article_id)
        )
        """
    )


def downgrade():
    op.execute("DROP TABLE IF EXISTS article_like")
