"""
Database connection and session management.

This module provides utilities for managing database connections and sessions,
including both synchronous and asynchronous database operations.
"""
import logging
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session as SyncSession, sessionmaker
from sqlmodel import SQLModel, select

from app.core.config import settings
from app.core.logging import logger
from app.models import User, UserCreate

# Configure logging
logger = logging.getLogger(__name__)

# Create database engines
sync_engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.SQL_ECHO,
)

async_engine = create_async_engine(
    str(settings.ASYNC_SQLALCHEMY_DATABASE_URI),
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.SQL_ECHO,
)

# Session factories
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
    class_=SyncSession,
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Context managers for database sessions
@contextmanager
def get_db() -> Generator[SyncSession, None, None]:
    """
    Context manager for synchronous database sessions.
    
    Yields:
        SyncSession: A synchronous database session
        
    Example:
        with get_db() as db:
            db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        db.close()


@asynccontextmanager
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for asynchronous database sessions.
    
    Yields:
        AsyncSession: An asynchronous database session
        
    Example:
        async with get_async_db() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Async database error: {str(e)}")
            raise
        finally:
            await session.close()


def get_sync_session() -> SyncSession:
    """
    Get a synchronous database session.
    
    Returns:
        SyncSession: A synchronous database session
        
    Note:
        Remember to close the session when done using session.close()
    """
    return SessionLocal()


async def get_async_session() -> AsyncSession:
    """
    Get an asynchronous database session.
    
    Returns:
        AsyncSession: An asynchronous database session
        
    Note:
        Remember to close the session when done using await session.close()
    """
    return AsyncSessionLocal()


# Database initialization
def init_db() -> None:
    """
    Initialize the database with default data.
    
    This function creates the database tables and adds an initial admin user
    if it doesn't already exist.
    """
    try:
        # Create all tables
        SQLModel.metadata.create_all(sync_engine)
        logger.info("Database tables created successfully")
        
        # Create default admin user if it doesn't exist
        with get_db() as session:
            # Check if admin user already exists
            stmt = select(User).where(User.email == settings.FIRST_SUPERUSER)
            result = session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                # Create admin user
                admin_user = User(
                    email=settings.FIRST_SUPERUSER,
                    hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                    is_active=True,
                    is_superuser=True,
                    is_verified=True,
                )
                session.add(admin_user)
                session.commit()
                logger.info(f"Created admin user: {settings.FIRST_SUPERUSER}")
            else:
                logger.info(f"Admin user already exists: {settings.FIRST_SUPERUSER}")
                
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise


async def async_init_db() -> None:
    """
    Asynchronously initialize the database with default data.
    
    This function creates the database tables and adds an initial admin user
    if it doesn't already exist.
    """
    try:
        # Create all tables
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database tables created successfully")
        
        # Create default admin user if it doesn't exist
        async with get_async_db() as session:
            # Check if admin user already exists
            stmt = select(User).where(User.email == settings.FIRST_SUPERUSER)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                # Create admin user
                admin_user = User(
                    email=settings.FIRST_SUPERUSER,
                    hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                    is_active=True,
                    is_superuser=True,
                    is_verified=True,
                )
                session.add(admin_user)
                await session.commit()
                logger.info(f"Created admin user: {settings.FIRST_SUPERUSER}")
            else:
                logger.info(f"Admin user already exists: {settings.FIRST_SUPERUSER}")
                
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise


def get_password_hash(password: str) -> str:
    """
    Generate a password hash.
    
    Args:
        password: The plain text password
        
    Returns:
        str: The hashed password
    """
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)
