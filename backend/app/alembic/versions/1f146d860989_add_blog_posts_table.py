"""add_blog_posts_table

Revision ID: 1f146d860989
Revises: e2c70adc2cef
Create Date: 2026-03-25 14:59:01.047819

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1f146d860989'
down_revision = 'e2c70adc2cef'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('blog_posts',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('slug', sa.String(length=200), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('excerpt', sa.Text(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('category', sa.String(length=50), nullable=False),
    sa.Column('read_time_minutes', sa.Integer(), nullable=False),
    sa.Column('author_name', sa.String(length=200), nullable=False),
    sa.Column('is_published', sa.Boolean(), nullable=False),
    sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_index('idx_blog_posts_published', 'blog_posts', ['is_published', 'published_at'], unique=False)


def downgrade():
    op.drop_index('idx_blog_posts_published', table_name='blog_posts')
    op.drop_table('blog_posts')
