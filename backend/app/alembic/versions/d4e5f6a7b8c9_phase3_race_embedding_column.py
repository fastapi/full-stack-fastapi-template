"""Phase 3: add embedding vector column to race table

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-04-23 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # pgvector extension must already exist (applied in c3d4e5f6a7b8)
    op.execute("ALTER TABLE race ADD COLUMN IF NOT EXISTS embedding vector(1536);")
    # IVFFlat index for approximate nearest-neighbour search (cosine distance)
    # lists=100 is a reasonable default for up to ~1M rows
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_race_embedding_ivfflat "
        "ON race USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_race_embedding_ivfflat;")
    op.execute("ALTER TABLE race DROP COLUMN IF EXISTS embedding;")
