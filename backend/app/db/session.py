from typing import Generator

from sqlmodel import Session, create_engine

from app.core.config import settings

# PostgreSQL Connection
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def get_session() -> Generator[Session, None, None]:
    """Get a SQLModel session for PostgreSQL database operations."""
    with Session(engine) as session:
        yield session 