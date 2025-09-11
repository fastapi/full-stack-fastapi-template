"""Initial data creation script."""

import logging

from sqlmodel import Session

from app.core.db import engine, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    """Initialize database with initial data."""
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    """Run initial data creation."""
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
