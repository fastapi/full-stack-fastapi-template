import logging

from sqlalchemy import Engine
from sqlmodel import Session, select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.db import engine

# Configure logging to display INFO level messages
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
    Initialize the database.

    Attempts to create a session and execute a simple query to check if the database is awake.
    This function is not protected and can be called directly.

    Args:
        db_engine: The SQLAlchemy engine instance to use for database connection.

    Returns:
        None

    Raises:
        Exception: If there's an error during database initialization.

    Notes:
        This function uses a retry decorator to attempt initialization multiple times.
    """
    try:
        # Try to create session to check if DB is awake
        with Session(db_engine) as session:
            session.exec(select(1))
    except Exception as e:
        # Log any errors that occur during initialization
        logger.error(e)
        raise e
    finally:
        # Ensure the session is closed and any open transactions are rolled back
        session.rollback()
        session.close()


def main() -> None:
    """
    Initialize the service.

    Logs the start of service initialization, calls the init function to initialize the database,
    and logs the completion of the process. This function is not protected and can be called directly.

    Args:
        None

    Returns:
        None

    Notes:
        This function uses logging to provide information about the initialization process.
    """
    # Log the start of service initialization
    logger.info("Initializing service")
    # Call the init function with the engine to initialize the database
    init(engine)
    # Log the completion of service initialization
    logger.info("Service finished initializing")


# Entry point of the script
if __name__ == "__main__":
    # Call the main function when the script is run directly
    main()
