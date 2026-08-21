"""add rbac roles and permissions

Revision ID: 2d1ae9889b29
Revises: fe56fa70289e
Create Date: 2026-08-20 15:22:27.932585

"""
import uuid

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '2d1ae9889b29'
down_revision = 'fe56fa70289e'
branch_labels = None
depends_on = None


ADMIN_ROLE_ID = uuid.uuid4()
MANAGER_ROLE_ID = uuid.uuid4()
MEMBER_ROLE_ID = uuid.uuid4()

PERMISSION_CODES = [
    "users:list",
    "users:create",
    "users:manage",
    "metrics:view",
    "system:admin",
]

# role slug -> permission codes granted to it
ROLE_PERMISSIONS = {
    "admin": PERMISSION_CODES,
    "manager": ["users:list", "metrics:view"],
    "member": [],
}


def upgrade():
    op.create_table(
        'permission',
        sa.Column('code', sqlmodel.sql.sqltypes.AutoString(length=64), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_permission_code'), 'permission', ['code'], unique=True)
    op.create_table(
        'role',
        sa.Column('slug', sqlmodel.sql.sqltypes.AutoString(length=64), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_role_slug'), 'role', ['slug'], unique=True)
    op.create_table(
        'role_permission',
        sa.Column('role_id', sa.Uuid(), nullable=False),
        sa.Column('permission_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permission.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['role.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id'),
    )
    op.add_column('user', sa.Column('role_id', sa.Uuid(), nullable=True))

    bind = op.get_bind()

    role_table = sa.table('role', sa.column('id', sa.Uuid()), sa.column('slug', sa.String()))
    permission_table = sa.table(
        'permission', sa.column('id', sa.Uuid()), sa.column('code', sa.String())
    )
    role_permission_table = sa.table(
        'role_permission',
        sa.column('role_id', sa.Uuid()),
        sa.column('permission_id', sa.Uuid()),
    )

    role_ids = {
        "admin": ADMIN_ROLE_ID,
        "manager": MANAGER_ROLE_ID,
        "member": MEMBER_ROLE_ID,
    }
    bind.execute(
        role_table.insert(),
        [{"id": role_id, "slug": slug} for slug, role_id in role_ids.items()],
    )

    permission_ids = {code: uuid.uuid4() for code in PERMISSION_CODES}
    bind.execute(
        permission_table.insert(),
        [{"id": pid, "code": code} for code, pid in permission_ids.items()],
    )

    bind.execute(
        role_permission_table.insert(),
        [
            {"role_id": role_ids[slug], "permission_id": permission_ids[code]}
            for slug, codes in ROLE_PERMISSIONS.items()
            for code in codes
        ],
    )

    bind.execute(
        sa.text('UPDATE "user" SET role_id = :role_id WHERE is_superuser IS TRUE'),
        {"role_id": ADMIN_ROLE_ID},
    )
    bind.execute(
        sa.text(
            'UPDATE "user" SET role_id = :role_id '
            'WHERE is_superuser IS NOT TRUE'
        ),
        {"role_id": MEMBER_ROLE_ID},
    )

    op.alter_column('user', 'role_id', nullable=False)
    op.create_foreign_key(
        'user_role_id_fkey', 'user', 'role', ['role_id'], ['id']
    )
    op.drop_column('user', 'is_superuser')


def downgrade():
    op.add_column(
        'user',
        sa.Column(
            'is_superuser',
            sa.BOOLEAN(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    bind = op.get_bind()
    bind.execute(
        sa.text(
            'UPDATE "user" SET is_superuser = true '
            'WHERE role_id = (SELECT id FROM role WHERE slug = \'admin\')'
        )
    )
    op.alter_column('user', 'is_superuser', server_default=None)

    op.drop_constraint('user_role_id_fkey', 'user', type_='foreignkey')
    op.drop_column('user', 'role_id')
    op.drop_table('role_permission')
    op.drop_index(op.f('ix_role_slug'), table_name='role')
    op.drop_table('role')
    op.drop_index(op.f('ix_permission_code'), table_name='permission')
    op.drop_table('permission')
