#!/usr/bin/env python3
"""
Script to test Alembic migrations in an isolated environment.
This script:
1. Creates a temporary database
2. Applies the migrations
3. Verifies that the tables were created correctly
4. Rolls back the migrations
5. Verifies that the tables were dropped correctly
"""
import os
import sys
import tempfile
import subprocess
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import NullPool
from alembic.config import Config
from alembic import command

# Configuration
ALEMBIC_INI = Path(__file__).parent.parent / "alembic.ini"
MIGRATIONS_DIR = Path(__file__).parent.parent / "app" / "alembic"


def create_temp_db():
    """Create a temporary SQLite database for testing migrations."""
    temp_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db_file.close()
    db_url = f"sqlite:///{temp_db_file.name}"
    
    # Create a custom alembic.ini file for the test
    temp_alembic_ini = tempfile.NamedTemporaryFile(suffix=".ini", delete=False)
    with open(ALEMBIC_INI, "r") as original:
        content = original.read()
        # Replace the SQLAlchemy URL with our temporary database
        content = content.replace(
            "sqlalchemy.url = driver://user:pass@localhost/dbname",
            f"sqlalchemy.url = {db_url}"
        )
    
    with open(temp_alembic_ini.name, "w") as temp:
        temp.write(content)
    
    return db_url, temp_db_file.name, temp_alembic_ini.name


def get_alembic_config(alembic_ini):
    """Get the Alembic configuration."""
    config = Config(alembic_ini)
    config.set_main_option("script_location", str(MIGRATIONS_DIR))
    return config


def check_tables(engine, expected_tables):
    """Check if the expected tables exist in the database."""
    inspector = inspect(engine)
    actual_tables = inspector.get_table_names()
    
    print(f"Expected tables: {sorted(expected_tables)}")
    print(f"Actual tables: {sorted(actual_tables)}")
    
    missing_tables = set(expected_tables) - set(actual_tables)
    extra_tables = set(actual_tables) - set(expected_tables)
    
    if missing_tables:
        print(f"ERROR: Missing tables: {missing_tables}")
        return False
    
    if extra_tables:
        print(f"WARNING: Extra tables found: {extra_tables}")
    
    return True


def test_migrations():
    """Test the migrations by applying them and then rolling them back."""
    print("Testing migrations in an isolated environment...")
    
    # Create a temporary database
    db_url, db_file, alembic_ini = create_temp_db()
    print(f"Created temporary database at: {db_file}")
    
    try:
        # Create engine
        engine = create_engine(db_url, poolclass=NullPool)
        
        # Get Alembic config
        config = get_alembic_config(alembic_ini)
        
        # Apply all migrations
        print("\nApplying migrations...")
        command.upgrade(config, "head")
        print("Migrations applied successfully.")
        
        # Check if all expected tables exist
        expected_tables = [
            "user", "item", "userfollow", "workoutpost", 
            "workout", "exercise"
        ]
        
        print("\nChecking if all tables were created...")
        if not check_tables(engine, expected_tables):
            print("ERROR: Not all expected tables were created.")
            return False
        
        print("All expected tables were created successfully.")
        
        # Test some basic operations
        print("\nTesting basic database operations...")
        with engine.connect() as conn:
            # Check user table structure
            user_columns = inspect(engine).get_columns("user")
            user_column_names = [col["name"] for col in user_columns]
            print(f"User table columns: {user_column_names}")
            
            # Check workout table structure
            workout_columns = inspect(engine).get_columns("workout")
            workout_column_names = [col["name"] for col in workout_columns]
            print(f"Workout table columns: {workout_column_names}")
            
            # Check exercise table structure
            exercise_columns = inspect(engine).get_columns("exercise")
            exercise_column_names = [col["name"] for col in exercise_columns]
            print(f"Exercise table columns: {exercise_column_names}")
            
            # Check foreign keys
            workout_fks = inspect(engine).get_foreign_keys("workout")
            exercise_fks = inspect(engine).get_foreign_keys("exercise")
            
            print(f"Workout foreign keys: {workout_fks}")
            print(f"Exercise foreign keys: {exercise_fks}")
        
        # Roll back all migrations
        print("\nRolling back migrations...")
        command.downgrade(config, "base")
        print("Migrations rolled back successfully.")
        
        # Check if all tables were dropped
        print("\nChecking if all tables were dropped...")
        inspector = inspect(engine)
        remaining_tables = inspector.get_table_names()
        
        if remaining_tables:
            print(f"ERROR: Some tables remain after downgrade: {remaining_tables}")
            return False
        
        print("All tables were dropped successfully.")
        
        print("\nMigration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"ERROR: Migration test failed: {e}")
        return False
        
    finally:
        # Clean up temporary files
        try:
            os.unlink(db_file)
            os.unlink(alembic_ini)
            print(f"\nCleaned up temporary files.")
        except Exception as e:
            print(f"WARNING: Failed to clean up temporary files: {e}")


if __name__ == "__main__":
    success = test_migrations()
    sys.exit(0 if success else 1)