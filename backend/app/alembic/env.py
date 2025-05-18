"""
Alembic environment configuration.

This module configures the Alembic environment for database migrations.
"""
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
fileConfig(config.config_file_name)

# Import models from all modules for Alembic to detect schema changes
from app.core.config import settings  # noqa: E402
from app.core.logging import get_logger  # noqa: E402

# Import all models
# Keep the legacy import for now - this is sufficient for initial migrations
from app.models import *  # noqa: F403, F401

# NOTE: During the transition to a modular architecture, we're only importing the
# legacy models to avoid table definition conflicts. Once the transition is complete,
# we'll replace this with imports from each module.
#
# DO NOT uncomment these imports until all legacy model references are removed and
# the transition to modular models is complete.
#
# # Import models from modules
# # Auth module models
# # from app.modules.auth.domain.models import *  # noqa: F403, F401
# # Users module models
# # from app.modules.users.domain.models import *  # noqa: F403, F401
# # Items module models
# # from app.modules.items.domain.models import *  # noqa: F403, F401

# Set up target metadata
target_metadata = SQLModel.metadata

# Initialize logger
logger = get_logger("alembic")


def get_url() -> str:
    """
    Get database URL from settings.
    
    Returns:
        Database URL string
    """
    return str(settings.SQLALCHEMY_DATABASE_URI)


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.
    
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_url()
    context.configure(
        url=url, 
        target_metadata=target_metadata, 
        literal_binds=True, 
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    
    In this scenario we need to create an Engine and associate
    a connection with the context.
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
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()


# Run migrations based on mode
if context.is_offline_mode():
    logger.info("Running migrations in offline mode")
    run_migrations_offline()
else:
    logger.info("Running migrations in online mode")
    run_migrations_online()