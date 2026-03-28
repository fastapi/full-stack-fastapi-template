"""Add media assets table

Revision ID: 2a7b0f12d4ef
Revises: 15962f3dcaee
Create Date: 2026-03-29 11:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "2a7b0f12d4ef"
down_revision = "15962f3dcaee"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "mediaasset",
        sa.Column("content_type", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("content_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column("alt_text", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("original_filename", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("file_name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("file_path", sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=False),
        sa.Column("file_url", sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=False),
        sa.Column("mime_type", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("uploaded_by_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["uploaded_by_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mediaasset_content_type"), "mediaasset", ["content_type"], unique=False)
    op.create_index(op.f("ix_mediaasset_content_id"), "mediaasset", ["content_id"], unique=False)
    op.create_index(op.f("ix_mediaasset_kind"), "mediaasset", ["kind"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_mediaasset_kind"), table_name="mediaasset")
    op.drop_index(op.f("ix_mediaasset_content_id"), table_name="mediaasset")
    op.drop_index(op.f("ix_mediaasset_content_type"), table_name="mediaasset")
    op.drop_table("mediaasset")
