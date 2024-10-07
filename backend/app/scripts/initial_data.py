import logging

from sqlmodel import Session

from app.core.db import engine, init_db

# Configure logging to display INFO level messages
logging.basicConfig(level=logging.INFO)
# Create a logger instance for this module
logger = logging.getLogger(__name__)


def init() -> None:
    """
    Initialize the database with initial data.

    Creates a new database session and calls the init_db function to set up the initial database state.
    This function is not protected and can be called directly.

    Args:
        None

    Returns:
        None

    Raises:
        SQLAlchemyError: If there's an error during database operations.

    Notes:
        This function uses a context manager to ensure proper handling of the database session.
    """
    # Create a new database session
    with Session(engine) as session:
        # Call the init_db function to set up the initial database state
        init_db(session)


def main() -> None:
    """
    Main function to create initial data.

    Logs the start of the data creation process, calls the init function to initialize the database,
    and logs the completion of the process. This function is not protected and can be called directly.

    Args:
        None

    Returns:
        None

    Notes:
        This function uses logging to provide information about the data creation process.
    """
    # Log the start of the data creation process
    logger.info("Creating initial data")
    # Call the init function to initialize the database
    init()
    # Log the completion of the data creation process
    logger.info("Initial data created")


if __name__ == "__main__":
    """
    Entry point for the script.

    Executes the main function when the script is run directly.
    This block is not protected and will run if the script is executed as the main program.

    Args:
        None

    Returns:
        None

    Notes:
        This is a standard Python idiom for scripts that can be both imported and run directly.
    """
    # Execute the main function when the script is run directly
    main()
