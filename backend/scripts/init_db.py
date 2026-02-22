"""
Database initialization script for new environments.
Run this script to provision the database and tables.

Usage:
    python scripts/init_db.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.repo import Base
from app.config import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    # Connect to the default 'postgres' database to check/create our target DB
    password_part = f":{settings.pg_password}" if settings.pg_password else ""
    base_url = f"postgresql+asyncpg://{settings.pg_user}{password_part}@{settings.pg_host}:{settings.pg_port}/postgres"

    engine = create_async_engine(base_url, echo=False, isolation_level="AUTOCOMMIT")

    try:
        async with engine.connect() as conn:
            # Check if database exists
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                {"dbname": settings.pg_database}
            )
            db_exists = result.fetchone()

            if not db_exists:
                logger.info(f"Database '{settings.pg_database}' does not exist. Creating...")
                await conn.execute(
                    text(f'CREATE DATABASE "{settings.pg_database}"')
                )
                logger.info(f"Database '{settings.pg_database}' created successfully")
            else:
                logger.info(f"Database '{settings.pg_database}' already exists")

    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        raise
    finally:
        await engine.dispose()


async def create_tables():
    """Create all tables defined in the models"""
    engine = create_async_engine(
        settings.database_url,
        echo=True
    )

    try:
        async with engine.begin() as conn:
            logger.info("Creating tables...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Tables created successfully")

            # Verify tables were created
            result = await conn.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            )
            tables = result.fetchall()
            logger.info(f"Existing tables: {[table[0] for table in tables]}")

    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise
    finally:
        await engine.dispose()


async def verify_schema():
    """Verify the schema is correct"""
    engine = create_async_engine(settings.database_url, echo=False)

    try:
        async with engine.connect() as conn:
            # Check prompts table structure
            result = await conn.execute(
                text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = 'prompts' AND table_schema = 'public'
                    ORDER BY ordinal_position
                """)
            )
            columns = result.fetchall()

            logger.info("Prompts table structure:")
            for col in columns:
                logger.info(f"  {col[0]} - {col[1]} - Nullable: {col[2]} - Default: {col[3]}")

            # Check indexes
            result = await conn.execute(
                text("SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'prompts'")
            )
            indexes = result.fetchall()

            logger.info("Prompts table indexes:")
            for idx in indexes:
                logger.info(f"  {idx[0]}: {idx[1]}")

    except Exception as e:
        logger.error(f"Error verifying schema: {str(e)}")
        raise
    finally:
        await engine.dispose()


async def main():
    """Main initialization function"""
    try:
        logger.info("=" * 60)
        logger.info("Starting database initialization...")
        logger.info("=" * 60)

        logger.info(f"Target database: {settings.pg_database}")
        logger.info(f"Host: {settings.pg_host}:{settings.pg_port}")

        # Step 1: Create database if needed
        await create_database_if_not_exists()

        # Step 2: Create tables
        await create_tables()

        # Step 3: Verify schema
        await verify_schema()

        logger.info("=" * 60)
        logger.info("Database initialization completed successfully!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"Database initialization failed: {str(e)}")
        logger.error("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
