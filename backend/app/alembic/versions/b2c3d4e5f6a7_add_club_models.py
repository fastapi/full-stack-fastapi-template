"""Add club models

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-04

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Club table
    op.create_table(
        "club",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("cover_image_url", sa.String(length=1000), nullable=True),
        sa.Column("visibility", sa.String(length=20), nullable=False, server_default="public"),
        sa.Column("rules", sa.String(length=2000), nullable=True),
        sa.Column("theme_color", sa.String(length=20), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_club_name", "club", ["name"])

    # ClubMember table
    op.create_table(
        "club_member",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("club_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="member"),
        sa.Column(
            "joined_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["club_id"], ["club.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_club_member_club_id", "club_member", ["club_id"])
    op.create_index("ix_club_member_user_id", "club_member", ["user_id"])
    op.create_index(
        "ix_club_member_club_user", "club_member", ["club_id", "user_id"], unique=True
    )

    # ClubWatchlist table
    op.create_table(
        "club_watchlist",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("club_id", sa.Uuid(), nullable=False),
        sa.Column("movie_id", sa.Uuid(), nullable=False),
        sa.Column("added_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column(
            "added_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["club_id"], ["club.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["movie_id"], ["movie.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["added_by_user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_club_watchlist_club_id", "club_watchlist", ["club_id"])
    op.create_index(
        "ix_club_watchlist_club_movie", "club_watchlist", ["club_id", "movie_id"], unique=True
    )

    # ClubWatchlistVote table
    op.create_table(
        "club_watchlist_vote",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("watchlist_entry_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("vote_type", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["watchlist_entry_id"], ["club_watchlist.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_club_watchlist_vote_entry_id", "club_watchlist_vote", ["watchlist_entry_id"])
    op.create_index(
        "ix_club_watchlist_vote_entry_user",
        "club_watchlist_vote",
        ["watchlist_entry_id", "user_id"],
        unique=True,
    )

    # Add foreign key from rating to club
    op.create_foreign_key(
        "fk_rating_club_id",
        "rating",
        "club",
        ["club_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_rating_club_id", "rating", type_="foreignkey")
    op.drop_table("club_watchlist_vote")
    op.drop_table("club_watchlist")
    op.drop_table("club_member")
    op.drop_table("club")
