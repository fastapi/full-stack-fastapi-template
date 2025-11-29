import logging
import sys

from sqlmodel import Session

from app.core.db import engine, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    try:
        with Session(engine) as session:
            init_db(session)
    except Exception as e:
        logger.error(f"Error in init_db: {e}", exc_info=True)
        raise


def main() -> None:
    try:
        logger.info("Creating initial data")
        init()
        logger.info("Initial data created")
    except Exception as e:
        logger.error(f"Failed to create initial data: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
