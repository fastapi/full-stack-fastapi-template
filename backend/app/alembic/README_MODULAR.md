# Alembic in Modular Monolith Architecture

This document explains how to use Alembic with the modular monolith architecture.

## Overview

In our modular monolith architecture, models are distributed across multiple modules. This presents a challenge for Alembic, which needs to be aware of all models to generate migrations correctly.

## Current Architecture

The Alembic environment is configured to work with our modular structure:

1. **Table Models**: Table models (with `table=True`) are imported directly from their respective modules (e.g., `app.modules.users.domain.models.User`).
2. **Non-Table Models**: Non-table models (without `table=True`) are also imported from their respective modules.
3. **Centralized Metadata**: All models share the same SQLModel metadata, which Alembic uses to detect schema changes.

## Generating Migrations

To generate a migration:

```bash
# From the project root directory
alembic revision --autogenerate -m "description_of_changes"
```

## Applying Migrations

To apply migrations:

```bash
# Apply all pending migrations
alembic upgrade head

# Apply a specific number of migrations
alembic upgrade +1

# Rollback a specific number of migrations
alembic downgrade -1
```

## Handling Module-Specific Migrations

For module-specific migrations that don't affect the database schema (e.g., data migrations), you can create empty migrations:

```bash
alembic revision -m "data_migration_for_module_x"
```

Then edit the generated file to include your custom migration logic.

## Best Practices

1. **Run Tests After Migrations**: Always run tests after applying migrations to ensure the application still works.
2. **Keep Migrations Small**: Make small, focused changes to make migrations easier to understand and troubleshoot.
3. **Document Complex Migrations**: Add comments to explain complex migration logic.
4. **Version Control**: Always commit migration files to version control.

## Troubleshooting

If you encounter issues with Alembic:

1. **Import Errors**: Ensure all models are properly imported in `env.py`.
2. **Duplicate Tables**: Check for duplicate table definitions (models with the same `__tablename__`).
3. **Missing Dependencies**: Ensure all required packages are installed.
4. **Python Path**: Make sure the Python path includes the application root directory.
