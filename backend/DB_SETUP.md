# Database Setup and Migrations

This document explains how to set up the database and manage migrations for the Copilot backend.

## Prerequisites

- Python 3.8+
- PostgreSQL 13+
- pip
- virtualenv (recommended)

## Setup

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Set up environment variables**:
   Copy `.env.example` to `.env` and update the values:
   ```bash
   cp .env.example .env
   ```

## Database Configuration

Update the following environment variables in your `.env` file:

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/copilot
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/copilot
```

## Running Migrations

### Create a new migration

To create a new migration after making changes to your models:

```bash
python -m scripts.migrate create --message "your migration message"
```

### Apply migrations

To apply all pending migrations:

```bash
python -m scripts.migrate upgrade head
```

### Rollback a migration

To rollback to a previous migration:

```bash
python -m scripts.migrate downgrade <revision>
```

### Show current migration

To show the current migration:

```bash
python -m scripts.migrate current
```

### Show migration history

To show the migration history:

```bash
python -m scripts.migrate history
```

## Initial Setup

To set up the database and run all migrations:

```bash
./scripts/setup_db.sh
```

This will:
1. Check if the database is accessible
2. Run all pending migrations
3. Create an initial admin user if it doesn't exist

## Database Models

The database models are defined in `app/models/`:

- `base.py`: Base model classes and mixins
- `user.py`: User-related models and schemas

## Common Issues

### Database Connection Issues

If you encounter connection issues:

1. Ensure PostgreSQL is running
2. Check that the database exists and the user has the correct permissions
3. Verify the connection string in your `.env` file

### Migration Issues

If you encounter issues with migrations:

1. Make sure all models are properly imported in `app/models/__init__.py`
2. Check for any syntax errors in your models
3. If needed, you can delete the migration files in `app/alembic/versions/` and create a new initial migration
