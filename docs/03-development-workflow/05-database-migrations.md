# Database Migrations

This guide explains how to use Alembic for database migrations in the modular monolith architecture.

## Overview

Database migrations allow you to evolve your database schema over time as your application grows and changes. In our architecture, we use [Alembic](https://alembic.sqlalchemy.org/) integrated with SQLModel for managing migrations.

The key challenge in our modular structure is that domain models are distributed across multiple modules, but Alembic needs to be aware of all models to generate migrations correctly.

## Migration Architecture

The migration system is configured to work with our modular structure:

1. **Centralized Alembic**: There is a single Alembic configuration in `backend/app/alembic/`
2. **Model Discovery**: All models from different modules are imported in the Alembic environment
3. **Single Metadata**: All SQLModel models share the same metadata, which Alembic uses to detect schema changes

## Directory Structure

```
backend/
├── app/
│   ├── alembic/
│   │   ├── env.py                    # Alembic environment config
│   │   ├── migration_template.py.mako # Template for new migrations
│   │   └── versions/                 # Migration script files
│   │       ├── 1a31ce608336_add_cascade_delete_relationships.py
│   │       ├── 9c0a54914c78_add_max_length_for_string_varchar_.py
│   │       └── ...
```

## Creating Migrations

### Automatic Migration Generation

After making changes to your models, generate a migration with:

```bash
# Using Docker Compose
docker compose exec backend bash -c "alembic revision --autogenerate -m 'description_of_changes'"

# Local development
cd backend
alembic revision --autogenerate -m "description_of_changes"
```

The `--autogenerate` flag tells Alembic to compare the models against the database and generate migration operations automatically.

### Manual Migration Creation

For complex migrations or data migrations that don't involve schema changes, create an empty migration:

```bash
docker compose exec backend bash -c "alembic revision -m 'data_migration_description'"
```

Then edit the generated file to add your custom migration logic.

## Applying Migrations

### Apply All Pending Migrations

```bash
# Using Docker Compose
docker compose exec backend bash -c "alembic upgrade head"

# Local development
cd backend
alembic upgrade head
```

### Apply Specific Number of Migrations

```bash
# Apply next migration
docker compose exec backend bash -c "alembic upgrade +1"

# Apply next 3 migrations
docker compose exec backend bash -c "alembic upgrade +3"
```

### Rollback Migrations

```bash
# Rollback last migration
docker compose exec backend bash -c "alembic downgrade -1"

# Rollback to a specific revision
docker compose exec backend bash -c "alembic downgrade 9c0a54914c78"
```

## Adding Models From New Modules

When you create a new module with its own models, ensure they're included in the migration process:

1. Import the model in `backend/app/alembic/env.py` for auto-discovery
2. Test that the model is properly discovered by generating a migration
3. Verify that the migration creates the expected schema changes

## Best Practices

### 1. Keep Migrations Small

Make small, focused changes to make migrations easier to understand and troubleshoot.

### 2. Run Tests After Migrations

Always run tests after applying migrations to ensure the application still works:

```bash
docker compose exec backend bash scripts/tests-start.sh
```

### 3. Document Complex Migrations

Add comments to explain complex migration logic, especially for:
- Data migrations
- Changes that require special handling
- Performance considerations for large tables

Example:
```python
# op.execute() for large tables can be slow - consider batching
with op.batch_alter_table("user", schema=None) as batch_op:
    batch_op.add_column(sa.Column("new_column", sa.String(), nullable=True))
```

### 4. Always Version Control Migrations

Ensure all migration files are committed to version control to maintain a consistent database schema across environments.

### 5. Handle SQLModel Specifics

When working with SQLModel, remember:
- SQLModel models must have `table=True` to be included in migrations
- Field types should be compatible with SQLAlchemy
- Be careful with relationships to ensure they're defined correctly

## Common Migration Operations

### Adding a Column

```python
def upgrade():
    op.add_column('user', sa.Column('new_column', sa.String(255), nullable=True))

def downgrade():
    op.drop_column('user', 'new_column')
```

### Modifying a Column

```python
def upgrade():
    op.alter_column('user', 'email',
                    existing_type=sa.String(length=255),
                    type_=sa.String(length=320),
                    nullable=False)

def downgrade():
    op.alter_column('user', 'email',
                    existing_type=sa.String(length=320),
                    type_=sa.String(length=255),
                    nullable=True)
```

### Adding an Index

```python
def upgrade():
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_user_email'), table_name='user')
```

### Data Migration

```python
def upgrade():
    # Get binding and create a session
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    
    try:
        # Fetch all users
        users = session.execute(sa.text("SELECT id, full_name FROM \"user\"")).fetchall()
        
        # Update data
        for user_id, full_name in users:
            if full_name:
                # Capitalize names
                capitalized = full_name.title()
                session.execute(
                    sa.text("UPDATE \"user\" SET full_name = :full_name WHERE id = :id"),
                    {"full_name": capitalized, "id": user_id}
                )
        
        # Commit changes
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def downgrade():
    # Data migrations often don't have a downgrade path
    pass
```

## Troubleshooting

### Import Errors

If you encounter import errors during auto-generation:

1. Ensure all models are properly imported in `backend/app/alembic/env.py`
2. Check for circular imports in your model files
3. Use absolute imports in your model files

### Duplicate Tables

If you get errors about duplicate table definitions:

1. Check for models with the same `__tablename__` in different modules
2. Ensure each table name is unique across all modules

### Empty Migration

If auto-generated migrations are empty even though you made model changes:

1. Verify the models have `table=True`
2. Check that the models are properly imported in `env.py`
3. Make sure you're connected to the right database
4. Try running `alembic stamp head` to reset the migration state if the database is new or empty

### Migration Fails to Apply

If a migration fails when applying:

1. Check the database state to see what went wrong
2. Fix the issue in a new migration rather than editing the failed one
3. If necessary, use `alembic stamp <revision>` to mark a migration as applied without actually running it