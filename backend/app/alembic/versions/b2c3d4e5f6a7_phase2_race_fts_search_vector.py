"""Phase 2: add full-text search vector column and GIN index to race table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-21 01:00:00.000000

"""

from alembic import op

revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Generated stored tsvector column combining searchable text fields.
    # The GIN index makes full-text queries fast even on large tables.
    op.execute("""
        ALTER TABLE race
            ADD COLUMN search_vector tsvector
            GENERATED ALWAYS AS (
                to_tsvector(
                    'english',
                    coalesce(name, '') || ' ' ||
                    coalesce(description, '') || ' ' ||
                    coalesce(city, '') || ' ' ||
                    coalesce(state, '') || ' ' ||
                    coalesce(country, '')
                )
            ) STORED
    """)
    op.execute(
        "CREATE INDEX race_search_vector_idx ON race USING GIN(search_vector)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS race_search_vector_idx")
    op.execute("ALTER TABLE race DROP COLUMN IF EXISTS search_vector")
