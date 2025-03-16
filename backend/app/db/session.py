from typing import Generator
import os
from pymongo import MongoClient

from sqlmodel import Session, create_engine

from app.core.config import settings

# PostgreSQL Connection
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def get_session() -> Generator[Session, None, None]:
    """Get a SQLModel session for PostgreSQL database operations."""
    with Session(engine) as session:
        yield session

# MongoDB Connection
mongodb_server = os.environ.get("MONGODB_SERVER", "localhost")
mongodb_port = int(os.environ.get("MONGODB_PORT", "27017"))
mongodb_user = os.environ.get("MONGODB_USER", "mongo")
mongodb_password = os.environ.get("MONGODB_PASSWORD", "mongo")
mongodb_database = os.environ.get("MONGODB_DATABASE", "political_analysis")

# Create MongoDB client
mongodb_uri = f"mongodb://{mongodb_user}:{mongodb_password}@{mongodb_server}:{mongodb_port}/{mongodb_database}"
mongodb_client = MongoClient(mongodb_uri)
mongodb = mongodb_client[mongodb_database] 