import logging

from sqlalchemy import Engine
from sqlmodel import Session, select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.db import engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define retry parameters
max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


# Decorator for retrying the database initialization
@retry(
    stop=stop_after_attempt(max_tries),  # Stop after max_tries attempts
    wait=wait_fixed(wait_seconds),  # Wait for wait_seconds between attempts
    before=before_log(logger, logging.INFO),  # Log before each attempt
    after=after_log(logger, logging.WARN),  # Log after each failed attempt
)
def init(db_engine: Engine) -> None:
    """
    Initialize the database

    Attempts to create a database session and execute a simple query to check if the database is awake.
    This function is decorated with retry to handle potential connection issues.

    Args:
        db_engine: The SQLAlchemy engine instance to connect to the database.

    Returns:
        None

    Raises:
        Exception: If there's an error during database initialization after all retry attempts.

    Notes:
        The function uses a retry decorator to attempt the initialization multiple times
        before giving up. It logs the initialization process and any errors that occur.
    """
    try:
        with Session(db_engine) as session:
            # Try to create session to check if DB is awake
            session.exec(select(1))
    except Exception as e:
        # Log any errors that occur during initialization
        logger.error(f"Database initialization error: {e}")
        raise
    finally:
        # Ensure the session is closed and any open transactions are rolled back
        session.rollback()
        session.close()


def main() -> None:
    """
    Main function to initialize the service

    Calls the init function to initialize the database and logs the process.

    Args:
        None

    Returns:
        None

    Raises:
        None

    Notes:
        This function is the entry point for the service initialization process.
        It logs the start and end of the initialization process.
    """
    logger.info("Initializing service")
    init(engine)  # Call the init function with the engine
    logger.info("Service finished initializing")


# Entry point of the script
if __name__ == "__main__":
    main()
