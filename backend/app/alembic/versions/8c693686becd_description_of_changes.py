"""Description of changes

Revision ID: 8c693686becd
Revises: 9e690425af2e
Create Date: 2024-10-23 23:16:40.093380

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '8c693686becd'
down_revision = '9e690425af2e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('nightclub', sa.Column('age_limit', sa.Integer(), nullable=True))
    op.add_column('venue', sa.Column('zomato_link', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('venue', sa.Column('swiggy_link', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.drop_column('venue', 'swiggylink')
    op.drop_column('venue', 'zomatolink')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('zomatolink', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('venue', sa.Column('swiggylink', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('venue', 'swiggy_link')
    op.drop_column('venue', 'zomato_link')
    op.drop_column('nightclub', 'age_limit')
    # ### end Alembic commands ###
