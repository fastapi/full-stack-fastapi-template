"""Add inventory management system tables

Revision ID: 2025102701_inv
Revises: 1a31ce608336
Create Date: 2025-10-27 01:00:00.000000

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op
from sqlalchemy import Numeric

# revision identifiers, used by Alembic.
revision = "2025102701_inv"
down_revision = "1a31ce608336"
branch_labels = None
depends_on = None


def upgrade():
    # Add role column to user table
    op.add_column(
        "user",
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            server_default="vendedor"
        )
    )

    # Create category table
    op.create_table(
        "category",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_category_name"), "category", ["name"], unique=True)
    op.create_index(op.f("ix_category_created_by"), "category", ["created_by"], unique=False)

    # Create product table
    op.create_table(
        "product",
        sa.Column("sku", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column("category_id", sa.Uuid(), nullable=True),
        sa.Column("unit_price", Numeric(10, 2), nullable=False),
        sa.Column("sale_price", Numeric(10, 2), nullable=False),
        sa.Column("unit_of_measure", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column("min_stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("current_stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["category.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sku"),
        sa.CheckConstraint("current_stock >= 0", name="check_current_stock_positive"),
        sa.CheckConstraint("min_stock >= 0", name="check_min_stock_positive"),
        sa.CheckConstraint("unit_price > 0", name="check_unit_price_positive"),
        sa.CheckConstraint("sale_price > 0", name="check_sale_price_positive"),
    )
    op.create_index(op.f("ix_product_sku"), "product", ["sku"], unique=True)
    op.create_index(op.f("ix_product_category_id"), "product", ["category_id"], unique=False)
    op.create_index(op.f("ix_product_created_by"), "product", ["created_by"], unique=False)
    op.create_index(op.f("ix_product_stock_levels"), "product", ["current_stock", "min_stock"], unique=False)

    # Create inventorymovement table
    op.create_table(
        "inventorymovement",
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("movement_type", sa.String(length=30), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("reference_number", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column("notes", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column("unit_price", Numeric(10, 2), nullable=True),
        sa.Column("movement_date", sa.DateTime(), nullable=False),
        sa.Column("total_amount", Numeric(10, 2), nullable=True),
        sa.Column("stock_before", sa.Integer(), nullable=False),
        sa.Column("stock_after", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("stock_before >= 0", name="check_stock_before_positive"),
        sa.CheckConstraint("stock_after >= 0", name="check_stock_after_positive"),
        sa.CheckConstraint("quantity != 0", name="check_quantity_not_zero"),
    )
    op.create_index(
        op.f("ix_inventorymovement_product_date"),
        "inventorymovement",
        ["product_id", sa.text("movement_date DESC")],
        unique=False
    )
    op.create_index(op.f("ix_inventorymovement_movement_type"), "inventorymovement", ["movement_type"], unique=False)
    op.create_index(op.f("ix_inventorymovement_created_by"), "inventorymovement", ["created_by"], unique=False)
    op.create_index(op.f("ix_inventorymovement_movement_date"), "inventorymovement", [sa.text("movement_date DESC")], unique=False)

    # Create alert table
    op.create_table(
        "alert",
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("alert_type", sa.String(length=20), nullable=False),
        sa.Column("current_stock", sa.Integer(), nullable=False),
        sa.Column("min_stock", sa.Integer(), nullable=False),
        sa.Column("notes", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column("is_resolved", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("resolved_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resolved_by"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("current_stock >= 0", name="check_alert_current_stock_positive"),
        sa.CheckConstraint("min_stock >= 0", name="check_alert_min_stock_positive"),
    )
    op.create_index(op.f("ix_alert_product_resolved"), "alert", ["product_id", "is_resolved"], unique=False)
    op.create_index(op.f("ix_alert_resolved_created"), "alert", ["is_resolved", sa.text("created_at DESC")], unique=False)
    op.create_index(op.f("ix_alert_type"), "alert", ["alert_type"], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f("ix_alert_type"), table_name="alert")
    op.drop_index(op.f("ix_alert_resolved_created"), table_name="alert")
    op.drop_index(op.f("ix_alert_product_resolved"), table_name="alert")
    op.drop_table("alert")

    op.drop_index(op.f("ix_inventorymovement_movement_date"), table_name="inventorymovement")
    op.drop_index(op.f("ix_inventorymovement_created_by"), table_name="inventorymovement")
    op.drop_index(op.f("ix_inventorymovement_movement_type"), table_name="inventorymovement")
    op.drop_index(op.f("ix_inventorymovement_product_date"), table_name="inventorymovement")
    op.drop_table("inventorymovement")

    op.drop_index(op.f("ix_product_stock_levels"), table_name="product")
    op.drop_index(op.f("ix_product_created_by"), table_name="product")
    op.drop_index(op.f("ix_product_category_id"), table_name="product")
    op.drop_index(op.f("ix_product_sku"), table_name="product")
    op.drop_table("product")

    op.drop_index(op.f("ix_category_created_by"), table_name="category")
    op.drop_index(op.f("ix_category_name"), table_name="category")
    op.drop_table("category")

    # Remove role column from user table
    op.drop_column("user", "role")
