"""Add movie watchlist rating models

Revision ID: a1b2c3d4e5f6
Revises: 1a31ce608336
Create Date: 2026-02-04

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "1a31ce608336"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Movie table - OMDB cache
    op.create_table(
        "movie",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("imdb_id", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("year", sa.String(length=10), nullable=True),
        sa.Column("rated", sa.String(length=20), nullable=True),
        sa.Column("released", sa.String(length=50), nullable=True),
        sa.Column("runtime", sa.String(length=20), nullable=True),
        sa.Column("genre", sa.String(length=255), nullable=True),
        sa.Column("director", sa.String(length=500), nullable=True),
        sa.Column("writer", sa.String(length=1000), nullable=True),
        sa.Column("actors", sa.String(length=1000), nullable=True),
        sa.Column("plot", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=255), nullable=True),
        sa.Column("country", sa.String(length=255), nullable=True),
        sa.Column("awards", sa.String(length=500), nullable=True),
        sa.Column("poster_url", sa.String(length=1000), nullable=True),
        sa.Column("imdb_rating", sa.String(length=10), nullable=True),
        sa.Column("imdb_votes", sa.String(length=20), nullable=True),
        sa.Column("box_office", sa.String(length=50), nullable=True),
        sa.Column(
            "fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("raw_data", postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_movie_imdb_id", "movie", ["imdb_id"], unique=True)

    # UserWatchlist table
    op.create_table(
        "user_watchlist",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("movie_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="want_to_watch"),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("watched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "added_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["movie_id"], ["movie.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_watchlist_user_id", "user_watchlist", ["user_id"])
    op.create_index(
        "ix_user_watchlist_user_movie", "user_watchlist", ["user_id", "movie_id"], unique=True
    )

    # Rating table
    op.create_table(
        "rating",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("movie_id", sa.Uuid(), nullable=False),
        sa.Column("club_id", sa.Uuid(), nullable=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["movie_id"], ["movie.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rating_user_id", "rating", ["user_id"])
    op.create_index("ix_rating_movie_id", "rating", ["movie_id"])
    op.create_index("ix_rating_user_movie", "rating", ["user_id", "movie_id"], unique=True)


def downgrade() -> None:
    op.drop_table("rating")
    op.drop_table("user_watchlist")
    op.drop_table("movie")
