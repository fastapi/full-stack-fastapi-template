"""Add template and generation models

Revision ID: 6f44bc66fd3f
Revises: fe56fa70289e
Create Date: 2026-02-21 23:20:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "6f44bc66fd3f"
down_revision = "fe56fa70289e"
branch_labels = None
depends_on = None


template_category_enum = sa.Enum(
    "cover_letter",
    "email",
    "proposal",
    "other",
    name="templatecategory",
)
template_language_enum = sa.Enum(
    "fr",
    "en",
    "zh",
    "other",
    name="templatelanguage",
)


def upgrade() -> None:
    bind = op.get_bind()
    template_category_enum.create(bind, checkfirst=True)
    template_language_enum.create(bind, checkfirst=True)

    op.create_table(
        "template",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", template_category_enum, nullable=False),
        sa.Column("language", template_language_enum, nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_archived", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "templateversion",
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("variables_schema", sa.JSON(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["template_id"], ["template.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["created_by"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("template_id", "version"),
    )

    op.create_table(
        "generation",
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("extracted_values", sa.JSON(), nullable=False),
        sa.Column("output_text", sa.Text(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["template_id"], ["template.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["template_version_id"], ["templateversion.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("generation")
    op.drop_table("templateversion")
    op.drop_table("template")

    bind = op.get_bind()
    template_language_enum.drop(bind, checkfirst=True)
    template_category_enum.drop(bind, checkfirst=True)
