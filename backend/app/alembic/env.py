import os
from logging.config import fileConfig

from alembic import context
from alembic.autogenerate import rewriter
from alembic.operations import ops
from sqlalchemy import engine_from_config, pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

from app.models import SQLModel  # noqa
from app.core.config import settings # noqa

target_metadata = SQLModel.metadata


# SAFETY HOOK: Prevent dangerous operations in autogenerate
# This prevents CREATE TABLE operations on tables that already exist
# and filters out empty migrations
writer = rewriter.Rewriter()


@writer.rewrites(ops.CreateTableOp)
def prevent_table_recreation(context, revision, op):
    """Prevent CREATE TABLE on tables that already exist in the database.

    This catches the bug where autogenerate generates CREATE TABLE instead of ALTER TABLE.
    If a table already exists, this will raise an error instead of silently dropping data.
    """
    inspector = context.connection.inspect()
    existing_tables = inspector.get_table_names()

    if op.table_name in existing_tables:
        raise ValueError(
            f"❌ MIGRATION SAFETY ERROR: Attempted to CREATE TABLE '{op.table_name}' "
            f"but it already exists in the database. This would DROP and recreate the table, "
            f"causing DATA LOSS. Instead, use ADD COLUMN operations.\n\n"
            f"To fix:\n"
            f"1. Delete this migration file\n"
            f"2. Run: alembic revision --autogenerate -m 'your message'\n"
            f"3. Verify the new migration uses ADD COLUMN instead of CREATE TABLE"
        )

    return op


def include_object(object, name, type_, reflected, compare_to):
    """Filter objects to include in autogenerate.

    This prevents false positives where autogenerate thinks tables need to be recreated.
    Only include objects that are defined in our SQLModel metadata.
    """
    # Always include our application tables
    if type_ == "table":
        # Skip alembic's own version table
        if name == "alembic_version":
            return False
        # Only include tables defined in our models
        return name in target_metadata.tables

    return True


def process_revision_directives(context, revision, directives):
    """Process migration directives before they're written to a file.

    This hook:
    1. Prevents empty migrations from being generated
    2. Applies the rewriter to catch dangerous operations
    3. Provides helpful error messages
    """
    # Prevent empty migrations
    if directives[0].upgrade_ops.is_empty():
        directives[:] = []
        print("⚠️  No changes detected - not generating an empty migration")
        return

    # Apply the rewriter to catch dangerous operations
    return writer.process_revision_directives(context, revision, directives)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    return str(settings.SQLALCHEMY_DATABASE_URI)


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_object=include_object,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
