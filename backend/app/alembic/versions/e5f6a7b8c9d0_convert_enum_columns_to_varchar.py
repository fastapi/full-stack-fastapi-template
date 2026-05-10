"""convert enum columns to varchar

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-04-24 00:00:00.000000

SQLModel with AutoString sends character varying, but earlier migrations created
these columns as PostgreSQL native enum types. This migration converts them all to
VARCHAR and (for race.status which stored uppercase names) lowercases existing data.
"""
from alembic import op
import sqlalchemy as sa


revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Columns that stored uppercase enum names — convert to lowercase varchar in one step
    # via USING clause (the only way to change type and transform data simultaneously)
    op.execute(
        "ALTER TABLE race ALTER COLUMN status TYPE VARCHAR USING LOWER(status::text)"
    )
    op.execute(
        "ALTER TABLE raceregistration ALTER COLUMN registration_status TYPE VARCHAR USING LOWER(registration_status::text)"
    )
    op.execute(
        "ALTER TABLE raceregistration ALTER COLUMN payment_status TYPE VARCHAR USING LOWER(payment_status::text)"
    )
    op.execute(
        "ALTER TABLE raceresult ALTER COLUMN status TYPE VARCHAR USING LOWER(status::text)"
    )

    # Columns that already stored lowercase values — just retype
    op.execute(
        "ALTER TABLE race ALTER COLUMN terrain_type TYPE VARCHAR USING terrain_type::text"
    )
    op.execute(
        "ALTER TABLE race ALTER COLUMN difficulty_level TYPE VARCHAR USING difficulty_level::text"
    )
    op.execute(
        "ALTER TABLE userprofile ALTER COLUMN fitness_level TYPE VARCHAR USING fitness_level::text"
    )
    op.execute(
        "ALTER TABLE userprofile ALTER COLUMN distance_preference TYPE VARCHAR USING distance_preference::text"
    )
    op.execute(
        "ALTER TABLE userprofile ALTER COLUMN terrain_preference TYPE VARCHAR USING terrain_preference::text"
    )
    op.execute(
        "ALTER TABLE userraceinteraction ALTER COLUMN action TYPE VARCHAR USING action::text"
    )

    # Drop the now-unused PostgreSQL enum types
    op.execute("DROP TYPE IF EXISTS racestatusenum")
    op.execute("DROP TYPE IF EXISTS registrationstatusenum")
    op.execute("DROP TYPE IF EXISTS paymentstatusenum")
    op.execute("DROP TYPE IF EXISTS resultstatusenum")
    op.execute("DROP TYPE IF EXISTS terrainenum")
    op.execute("DROP TYPE IF EXISTS difficultyenum")
    op.execute("DROP TYPE IF EXISTS fitnessenum")
    op.execute("DROP TYPE IF EXISTS distanceprefenum")
    op.execute("DROP TYPE IF EXISTS interactiontypeenum")


def downgrade() -> None:
    # Recreate enum types and cast back — data stays lowercase which matches enum values
    op.execute(
        "CREATE TYPE racestatusenum AS ENUM ('draft','published','registration_open','registration_closed','completed','cancelled')"
    )
    op.execute(
        "ALTER TABLE race ALTER COLUMN status TYPE racestatusenum USING status::racestatusenum"
    )

    op.execute(
        "CREATE TYPE registrationstatusenum AS ENUM ('pending','confirmed','cancelled','waitlist')"
    )
    op.execute(
        "ALTER TABLE raceregistration ALTER COLUMN registration_status TYPE registrationstatusenum USING registration_status::registrationstatusenum"
    )

    op.execute(
        "CREATE TYPE paymentstatusenum AS ENUM ('unpaid','paid','refunded','partial')"
    )
    op.execute(
        "ALTER TABLE raceregistration ALTER COLUMN payment_status TYPE paymentstatusenum USING payment_status::paymentstatusenum"
    )

    op.execute(
        "CREATE TYPE resultstatusenum AS ENUM ('finished','dnf','dns','dq')"
    )
    op.execute(
        "ALTER TABLE raceresult ALTER COLUMN status TYPE resultstatusenum USING status::resultstatusenum"
    )

    op.execute(
        "CREATE TYPE terrainenum AS ENUM ('road','trail','track','mixed')"
    )
    op.execute(
        "ALTER TABLE race ALTER COLUMN terrain_type TYPE terrainenum USING terrain_type::terrainenum"
    )
    op.execute(
        "ALTER TABLE race ALTER COLUMN difficulty_level TYPE difficultyenum USING difficulty_level::difficultyenum"
    )

    op.execute(
        "CREATE TYPE difficultyenum AS ENUM ('easy','moderate','hard','extreme')"
    )
    op.execute(
        "CREATE TYPE fitnessenum AS ENUM ('beginner','intermediate','advanced','elite')"
    )
    op.execute(
        "ALTER TABLE userprofile ALTER COLUMN fitness_level TYPE fitnessenum USING fitness_level::fitnessenum"
    )
    op.execute(
        "CREATE TYPE distanceprefenum AS ENUM ('short','mid','long','ultra')"
    )
    op.execute(
        "ALTER TABLE userprofile ALTER COLUMN distance_preference TYPE distanceprefenum USING distance_preference::distanceprefenum"
    )
    op.execute(
        "ALTER TABLE userprofile ALTER COLUMN terrain_preference TYPE terrainenum USING terrain_preference::terrainenum"
    )

    op.execute(
        "CREATE TYPE interactiontypeenum AS ENUM ('viewed','saved','unsaved','registered','shared')"
    )
    op.execute(
        "ALTER TABLE userraceinteraction ALTER COLUMN action TYPE interactiontypeenum USING action::interactiontypeenum"
    )
