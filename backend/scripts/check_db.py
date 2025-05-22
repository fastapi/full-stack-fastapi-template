"""
Database connection check script.
This script verifies that the database is accessible and properly configured.
"""
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

# Add the backend directory to the path so we can import our app
sys.path.append(str(Path(__file__).parent.parent))

# Import settings after ensuring the app is in the path
from app.core.config import settings
from app.core.logging import setup_logging

# Set up logging
logger = setup_logging()

def check_database_config() -> bool:
    """Check if the database configuration is valid."""
    required_vars = [
        'SQLALCHEMY_DATABASE_URI',
        'ASYNC_SQLALCHEMY_DATABASE_URI',
        'FIRST_SUPERUSER',
        'FIRST_SUPERUSER_PASSWORD',
    ]
    
    missing_vars = [var for var in required_vars if not getattr(settings, var, None)]
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("✅ Database configuration is valid")
    return True

def check_database_connection() -> bool:
    """Check if the database is accessible."""
    try:
        # Create an engine and connect to the database
        engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
        with engine.connect() as conn:
            # Execute a simple query to verify the connection
            result = conn.execute(text("SELECT 1"))
            if result.scalar() == 1:
                logger.info("✅ Database connection successful!")
                return True
            else:
                logger.error("❌ Database connection check failed: Unexpected result")
                return False
    except OperationalError as e:
        logger.error(f"❌ Database connection failed (OperationalError): {e}")
        return False
    except SQLAlchemyError as e:
        logger.error(f"❌ Database connection failed (SQLAlchemyError): {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Database connection failed (Unexpected error): {e}")
        return False

def check_database_version() -> bool:
    """Check the database version and compatibility."""
    try:
        engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
        with engine.connect() as conn:
            # Check PostgreSQL version
            if 'postgresql' in str(settings.SQLALCHEMY_DATABASE_URI).lower():
                result = conn.execute(text("SELECT version()"))
                version = result.scalar()
                logger.info(f"📊 Database version: {version}")
                
                # Check if the required extensions are installed
                try:
                    result = conn.execute(text("SELECT extname FROM pg_extension WHERE extname IN ('uuid-ossp', 'pgcrypto')"))
                    extensions = [row[0] for row in result.fetchall()]
                    logger.info(f"📦 Installed extensions: {', '.join(extensions) if extensions else 'None'}")
                    
                    # Install required extensions if missing
                    if 'uuid-ossp' not in extensions:
                        logger.warning("⚠️  Extension 'uuid-ossp' is not installed. Some features may not work correctly.")
                    if 'pgcrypto' not in extensions:
                        logger.warning("⚠️  Extension 'pgcrypto' is not installed. Some features may not work correctly.")
                except Exception as e:
                    logger.warning(f"⚠️  Could not check database extensions: {e}")
            
            return True
    except Exception as e:
        logger.warning(f"⚠️  Could not check database version: {e}")
        return False

def main():
    """Main function to run database checks."""
    print("🔍 Checking database configuration...")
    if not check_database_config():
        print("❌ Database configuration is invalid. Please check your .env file.")
        sys.exit(1)
    
    print("\n🔍 Testing database connection...")
    if not check_database_connection():
        print("\n❌ Database connection failed. Please check the following:")
        print(f"  1. Is the database server running?")
        print(f"  2. Does the database '{settings.SQLALCHEMY_DATABASE_URI.split('/')[-1]}' exist?")
        print(f"  3. Are the database credentials in your .env file correct?")
        print(f"  4. Is the database server accessible from this machine?")
        sys.exit(1)
    
    print("\n🔍 Checking database version and extensions...")
    check_database_version()
    
    print("\n✅ All database checks passed!")
    sys.exit(0)

if __name__ == "__main__":
    main()
