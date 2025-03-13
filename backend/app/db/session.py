from typing import Generator

from motor.motor_asyncio import AsyncIOMotorClient
from redis import Redis
from sqlmodel import Session, create_engine

from app.core.config import settings

# PostgreSQL Connection
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

# MongoDB Connection
mongodb_client = None
mongodb = None

# Redis Connection
redis_client = None


def get_session() -> Generator[Session, None, None]:
    """Get a SQLModel session for PostgreSQL database operations."""
    with Session(engine) as session:
        yield session


async def connect_to_mongo() -> None:
    """Connect to MongoDB when the application starts."""
    global mongodb_client, mongodb
    mongodb_client = AsyncIOMotorClient(str(settings.MONGODB_URL))
    mongodb = mongodb_client[settings.MONGODB_DATABASE]


async def close_mongo_connection() -> None:
    """Close MongoDB connection when the application stops."""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()


def get_redis() -> Redis:
    """Get a Redis client instance."""
    global redis_client
    if not redis_client:
        redis_client = Redis.from_url(str(settings.REDIS_URL))
    return redis_client


def close_redis_connection() -> None:
    """Close Redis connection when the application stops."""
    global redis_client
    if redis_client:
        redis_client.close() 