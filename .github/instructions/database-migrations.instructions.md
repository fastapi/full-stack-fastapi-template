---
description: "Instructions for working with database migrations using Alembic in the FastAPI template."
applyTo: "backend/alembic/**/*"
---

# Database Migration Instructions

## Alembic Migrations

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database migrations with SQLModel.

### Migration File Location

```
backend/
├── alembic.ini                    # Alembic configuration
└── app/
    └── alembic/
        ├── env.py                # Migration environment setup
        ├── script.py.mako        # Migration template
        └── versions/             # Migration files
            ├── xxxx_initial.py
            └── yyyy_add_field.py
```

## Common Migration Tasks

### Creating a New Migration

After modifying models in `backend/app/models.py`:

```bash
cd backend

# Activate virtual environment
source .venv/bin/activate

# Generate migration automatically (recommended)
alembic revision --autogenerate -m "Add user profile fields"

# Or create empty migration (for data migrations)
alembic revision -m "Migrate user data"
```

**What --autogenerate does:**
- Compares database schema with SQLModel models
- Generates migration with `upgrade()` and `downgrade()` functions
- Creates new file in `app/alembic/versions/`

### Migration File Structure

```python
"""Add user profile fields

Revision ID: abc123def456
Revises: xyz789
Create Date: 2024-03-28 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# Revision identifiers
revision = 'abc123def456'
down_revision = 'xyz789'  # Previous migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply changes to database."""
    # Add column
    op.add_column('user', sa.Column('bio', sa.String(length=500), nullable=True))
    
    # Create index
    op.create_index('ix_user_bio', 'user', ['bio'])
    
    # Add foreign key
    op.add_column('item', sa.Column('category_id', sa.UUID(), nullable=True))
    op.create_foreign_key(
        'fk_item_category', 
        'item', 
        'category', 
        ['category_id'], 
        ['id']
    )


def downgrade() -> None:
    """Revert changes."""
    op.drop_constraint('fk_item_category', 'item', type_='foreignkey')
    op.drop_column('item', 'category_id')
    op.drop_index('ix_user_bio', 'user')
    op.drop_column('user', 'bio')
```

### Applying Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific number of migrations forward
alembic upgrade +2

# Apply to specific revision
alembic upgrade abc123def456

# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic heads
```

### Reverting Migrations

```bash
# Revert last migration
alembic downgrade -1

# Revert all migrations
alembic downgrade base

# Revert to specific revision
alembic downgrade xyz789

# Revert specific number of migrations
alembic downgrade -2
```

## Migration Patterns

### Adding a Column

```python
def upgrade() -> None:
    op.add_column(
        'table_name',
        sa.Column('new_field', sa.String(length=255), nullable=True)
    )

def downgrade() -> None:
    op.drop_column('table_name', 'new_field')
```

### Adding a Required Column (with default)

```python
def upgrade() -> None:
    # Step 1: Add column as nullable
    op.add_column(
        'table_name',
        sa.Column('required_field', sa.String(length=255), nullable=True)
    )
    
    # Step 2: Set default values for existing rows
    op.execute("UPDATE table_name SET required_field = 'default' WHERE required_field IS NULL")
    
    # Step 3: Make column non-nullable
    op.alter_column('table_name', 'required_field', nullable=False)

def downgrade() -> None:
    op.drop_column('table_name', 'required_field')
```

### Renaming a Column

```python
def upgrade() -> None:
    op.alter_column('table_name', 'old_name', new_column_name='new_name')

def downgrade() -> None:
    op.alter_column('table_name', 'new_name', new_column_name='old_name')
```

### Adding an Index

```python
def upgrade() -> None:
    op.create_index('ix_table_field', 'table_name', ['field_name'])

def downgrade() -> None:
    op.drop_index('ix_table_field', 'table_name')
```

### Adding a Foreign Key

```python
def upgrade() -> None:
    op.add_column(
        'child_table',
        sa.Column('parent_id', sa.UUID(), nullable=True)
    )
    op.create_foreign_key(
        'fk_child_parent',
        'child_table',
        'parent_table',
        ['parent_id'],
        ['id'],
        ondelete='CASCADE'  # Optional: cascade delete
    )

def downgrade() -> None:
    op.drop_constraint('fk_child_parent', 'child_table', type_='foreignkey')
    op.drop_column('child_table', 'parent_id')
```

### Creating a New Table

```python
def upgrade() -> None:
    op.create_table(
        'new_table',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_new_table_name', 'new_table', ['name'])

def downgrade() -> None:
    op.drop_index('ix_new_table_name', 'new_table')
    op.drop_table('new_table')
```

### Data Migration

```python
from alembic import op
from sqlalchemy import text

def upgrade() -> None:
    # Migrate data
    op.execute(
        text("""
            UPDATE user 
            SET full_name = CONCAT(first_name, ' ', last_name)
            WHERE full_name IS NULL
        """)
    )

def downgrade() -> None:
    # Revert data migration
    op.execute(
        text("""
            UPDATE user 
            SET full_name = NULL
        """)
    )
```

### Adding Enum Type

```python
import enum
from sqlalchemy.dialects import postgresql

class StatusEnum(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

def upgrade() -> None:
    # Create enum type (PostgreSQL)
    status_enum = postgresql.ENUM('active', 'inactive', 'pending', name='status_enum')
    status_enum.create(op.get_bind())
    
    # Add column with enum
    op.add_column(
        'table_name',
        sa.Column('status', sa.Enum(StatusEnum), nullable=False, server_default='pending')
    )

def downgrade() -> None:
    op.drop_column('table_name', 'status')
    
    # Drop enum type
    status_enum = postgresql.ENUM(name='status_enum')
    status_enum.drop(op.get_bind())
```

## Best Practices

### 1. Always Review Auto-generated Migrations

```bash
# After generating migration
alembic revision --autogenerate -m "description"

# Check the generated file in app/alembic/versions/
# Review upgrade() and downgrade() functions
# Make manual adjustments if needed
```

**Common issues with --autogenerate:**
- Doesn't detect column renames (sees as drop + add)
- Doesn't detect table renames
- May miss some constraint changes
- Doesn't handle data migrations

### 2. Make Migrations Reversible

Always implement `downgrade()` function:

```python
def upgrade() -> None:
    op.add_column('user', sa.Column('bio', sa.String(500)))

def downgrade() -> None:
    op.drop_column('user', 'bio')  # Must be reversible!
```

### 3. Test Migrations

```bash
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Test upgrade again
alembic upgrade head
```

### 4. Use Descriptive Names

Good: `alembic revision --autogenerate -m "Add user bio and avatar fields"`
Bad: `alembic revision --autogenerate -m "Update user"`

### 5. Keep Migrations Small

- One logical change per migration
- Don't mix schema changes with data migrations
- Split large migrations into smaller ones

### 6. Handle Existing Data

When adding non-nullable columns:
1. Add as nullable first
2. Populate existing rows
3. Make non-nullable

### 7. Use Batch Operations for SQLite

For SQLite compatibility (local dev):

```python
def upgrade() -> None:
    with op.batch_alter_table('table_name') as batch_op:
        batch_op.add_column(sa.Column('new_field', sa.String(255)))
        batch_op.create_index('ix_table_new_field', ['new_field'])
```

## Troubleshooting

### Migration Conflicts

If you get "Multiple heads" error:

```bash
# See all heads
alembic heads

# Merge migrations
alembic merge heads -m "Merge migrations"
```

### Reset Database (Development Only)

```bash
# WARNING: Destroys all data!
alembic downgrade base
alembic upgrade head
```

Or use Docker:

```bash
docker compose down -v  # Removes volumes
docker compose up -d
```

### Check Migration SQL

See SQL without applying:

```bash
# Show SQL for next migration
alembic upgrade head --sql

# Show SQL for specific revision
alembic upgrade abc123:def456 --sql
```

### Fix Failed Migration

If migration fails midway:

```bash
# Check current revision
alembic current

# Manually fix database or migration file

# Stamp to specific revision (mark as complete without running)
alembic stamp abc123def456

# Continue from there
alembic upgrade head
```

## Environment-Specific Migrations

Migrations run in:
- **Development**: Local PostgreSQL (Docker)
- **Testing**: Test database (automatic in tests)
- **Production**: Production database (CI/CD)

**Never run migrations manually in production!** Use deployment scripts.

## Workflow Checklist

When adding new models/fields:

- [ ] Update models in `backend/app/models.py`
- [ ] Generate migration: `alembic revision --autogenerate -m "description"`
- [ ] Review generated migration file
- [ ] Test upgrade: `alembic upgrade head`
- [ ] Test downgrade: `alembic downgrade -1`
- [ ] Test upgrade again: `alembic upgrade head`
- [ ] Commit migration file to git
- [ ] Update tests if needed
- [ ] Regenerate frontend client: `bash scripts/generate-client.sh`

## Additional Resources

- Alembic Documentation: https://alembic.sqlalchemy.org/
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- Project Guide: `/backend/README.md`
