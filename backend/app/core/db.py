import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Text, DateTime, Index, Boolean, ForeignKey, func
from datetime import datetime, timezone
from app.config import settings
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


def _build_connect_args() -> dict:
    """Return SSL connect args for production; empty dict for dev/beta."""
    if settings.environment == "production":
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return {"ssl": ctx}
    return {}


# Database engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args=_build_connect_args(),
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Dependency for database sessions
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database - create tables if they don't exist"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified successfully")
