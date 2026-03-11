"""Add brand_user table and brand columns

Revision ID: c5e82d93f0b1
Revises: b4d91e2f7c3a
Create Date: 2026-03-10

"""
from alembic import op
import sqlalchemy as sa

revision = 'c5e82d93f0b1'
down_revision = 'b4d91e2f7c3a'
branch_labels = None
depends_on = None

def upgrade():
    # Add columns to brands table
    op.add_column('brands', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('brands', sa.Column('company_id', sa.String(100), nullable=True))
    op.add_column('brands', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_index('idx_brands_company_id', 'brands', ['company_id'])

    # Create brand_user table
    op.create_table(
        'brand_user',
        sa.Column('brand_id', sa.String(100), nullable=False),
        sa.Column('user_id', sa.String(100), nullable=False),
        sa.Column('user_role', sa.Enum('owner', 'monitor', name='projectrole'), nullable=False),
        sa.Column('created_datetime', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_datetime', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('brand_id', 'user_id', 'user_role', name='pk_brand_user'),
    )
    op.create_index('idx_brand_user_user_id', 'brand_user', ['user_id'])
    op.create_index('idx_brand_user_brand_id', 'brand_user', ['brand_id'])

    # Data migration — populate brand_user from project_user
    conn = op.get_bind()

    # Copy project_user rows → brand_user, resolving brand_id via brand_prompts
    conn.execute(sa.text("""
        INSERT INTO brand_user (brand_id, user_id, user_role, created_datetime, updated_datetime)
        SELECT DISTINCT
            bp.brand_id,
            pu.user_id,
            LOWER(pu.user_role)::projectrole,
            pu.created_datetime,
            pu.updated_datetime
        FROM project_user pu
        JOIN brand_prompts bp ON bp.project_id = pu.project_id
        WHERE bp.brand_id IS NOT NULL AND bp.brand_id != ''
        ON CONFLICT DO NOTHING
    """))

    # Copy description, company_id, is_active from projects → brands (via brand_prompts join)
    conn.execute(sa.text("""
        UPDATE brands b
        SET
            description = COALESCE(b.description, p.description),
            company_id = COALESCE(b.company_id, p.company_id),
            is_active = p.is_active
        FROM brand_prompts bp
        JOIN projects p ON p.project_id = bp.project_id
        WHERE b.brand_id = bp.brand_id
          AND bp.project_id IS NOT NULL
    """))

def downgrade():
    op.drop_index('idx_brand_user_user_id', 'brand_user')
    op.drop_index('idx_brand_user_brand_id', 'brand_user')
    op.drop_table('brand_user')
    op.drop_index('idx_brands_company_id', 'brands')
    op.drop_column('brands', 'is_active')
    op.drop_column('brands', 'company_id')
    op.drop_column('brands', 'description')
