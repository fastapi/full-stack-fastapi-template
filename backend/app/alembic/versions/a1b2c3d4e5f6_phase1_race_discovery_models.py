"""Phase 1: race discovery models - geo fields, tags, user profile, interactions

Revision ID: a1b2c3d4e5f6
Revises: 2a7b0f12d4ef
Create Date: 2026-04-21 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "2a7b0f12d4ef"
branch_labels = None
depends_on = None


def _create_enum_if_not_exists(name: str, *values: str) -> None:
    """Create a PostgreSQL enum type if it doesn't already exist."""
    vals = ", ".join(f"'{v}'" for v in values)
    op.execute(
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{name}') THEN
                CREATE TYPE {name} AS ENUM ({vals});
            END IF;
        END
        $$;
        """
    )


# Column-level type objects with create_type=False so SQLAlchemy never tries
# to emit CREATE TYPE statements automatically.
_terrain = PgEnum("road", "trail", "track", "mixed", name="terrainenum", create_type=False)
_difficulty = PgEnum("easy", "moderate", "hard", "extreme", name="difficultyenum", create_type=False)
_fitness = PgEnum("beginner", "intermediate", "advanced", "elite", name="fitnessenum", create_type=False)
_distpref = PgEnum("short", "mid", "long", "ultra", name="distanceprefenum", create_type=False)
_interaction = PgEnum(
    "viewed", "saved", "unsaved", "registered", "shared",
    name="interactiontypeenum", create_type=False,
)


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Create enum types idempotently via DO block
    # ------------------------------------------------------------------
    _create_enum_if_not_exists("terrainenum", "road", "trail", "track", "mixed")
    _create_enum_if_not_exists("difficultyenum", "easy", "moderate", "hard", "extreme")
    _create_enum_if_not_exists("fitnessenum", "beginner", "intermediate", "advanced", "elite")
    _create_enum_if_not_exists("distanceprefenum", "short", "mid", "long", "ultra")
    _create_enum_if_not_exists("interactiontypeenum", "viewed", "saved", "unsaved", "registered", "shared")

    # ------------------------------------------------------------------
    # race table — add geo and course-characteristic columns
    # ------------------------------------------------------------------
    op.add_column("race", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("race", sa.Column("longitude", sa.Float(), nullable=True))
    op.add_column("race", sa.Column("terrain_type", _terrain, nullable=True))
    op.add_column("race", sa.Column("difficulty_level", _difficulty, nullable=True))
    op.add_column("race", sa.Column("elevation_gain_m", sa.Integer(), nullable=True))
    op.add_column(
        "race",
        sa.Column(
            "is_certified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "race",
        sa.Column(
            "gpx_file_url",
            sqlmodel.sql.sqltypes.AutoString(length=1000),
            nullable=True,
        ),
    )
    op.add_column(
        "race",
        sa.Column(
            "website_url",
            sqlmodel.sql.sqltypes.AutoString(length=1000),
            nullable=True,
        ),
    )

    # ------------------------------------------------------------------
    # racetag table
    # ------------------------------------------------------------------
    op.create_table(
        "racetag",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column("slug", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_racetag_name", "racetag", ["name"], unique=True)
    op.create_index("ix_racetag_slug", "racetag", ["slug"], unique=True)

    # ------------------------------------------------------------------
    # racetaglink junction table
    # ------------------------------------------------------------------
    op.create_table(
        "racetaglink",
        sa.Column("race_id", sa.Uuid(), nullable=False),
        sa.Column("tag_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["race_id"], ["race.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["racetag.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("race_id", "tag_id"),
    )

    # ------------------------------------------------------------------
    # userprofile table
    # ------------------------------------------------------------------
    op.create_table(
        "userprofile",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("fitness_level", _fitness, nullable=True),
        sa.Column("distance_preference", _distpref, nullable=True),
        sa.Column("terrain_preference", _terrain, nullable=True),
        sa.Column("home_latitude", sa.Float(), nullable=True),
        sa.Column("home_longitude", sa.Float(), nullable=True),
        sa.Column(
            "home_city",
            sqlmodel.sql.sqltypes.AutoString(length=100),
            nullable=True,
        ),
        sa.Column("weekly_mileage_km", sa.Float(), nullable=True),
        sa.Column("goal_race_date", sa.Date(), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column(
            "is_onboarded",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_userprofile_user_id", "userprofile", ["user_id"], unique=True)

    # ------------------------------------------------------------------
    # userraceinteraction table
    # ------------------------------------------------------------------
    op.create_table(
        "userraceinteraction",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("race_id", sa.Uuid(), nullable=False),
        sa.Column("action", _interaction, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["race_id"], ["race.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_userraceinteraction_user_id", "userraceinteraction", ["user_id"]
    )
    op.create_index(
        "ix_userraceinteraction_race_id", "userraceinteraction", ["race_id"]
    )


def downgrade() -> None:
    op.drop_table("userraceinteraction")
    op.drop_table("userprofile")
    op.drop_table("racetaglink")
    op.drop_table("racetag")

    op.drop_column("race", "website_url")
    op.drop_column("race", "gpx_file_url")
    op.drop_column("race", "is_certified")
    op.drop_column("race", "elevation_gain_m")
    op.drop_column("race", "difficulty_level")
    op.drop_column("race", "terrain_type")
    op.drop_column("race", "longitude")
    op.drop_column("race", "latitude")

    op.execute("DROP TYPE IF EXISTS interactiontypeenum")
    op.execute("DROP TYPE IF EXISTS distanceprefenum")
    op.execute("DROP TYPE IF EXISTS fitnessenum")
    op.execute("DROP TYPE IF EXISTS difficultyenum")
    op.execute("DROP TYPE IF EXISTS terrainenum")
