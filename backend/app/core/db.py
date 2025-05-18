"""
Database setup and utilities.

This module provides database setup, connection management, and helper utilities
for interacting with the database.
"""
from contextlib import contextmanager
from typing import Any, Callable, Dict, Generator, Type, TypeVar

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.sql.expression import SelectOfScalar

# Set up SQLModel for better query performance
# This prevents SQLModel from overriding SQLAlchemy's select() with a version
# that doesn't use caching. See: https://github.com/tiangolo/sqlmodel/issues/189
SelectOfScalar.inherit_cache = True

from app.core.config import settings
from app.core.logging import get_logger

# Configure logger
logger = get_logger("db")

# Database engine
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_pre_ping=True,
    echo=settings.ENVIRONMENT == "local",
)

# Type variables for repository pattern
T = TypeVar('T')
ModelType = TypeVar('ModelType', bound=SQLModel)
CreateSchemaType = TypeVar('CreateSchemaType', bound=SQLModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=SQLModel)


def get_session() -> Generator[Session, None, None]:
    """
    Get a database session.
    
    This function yields a database session that is automatically closed
    when the caller is done with it.
    
    Yields:
        SQLModel Session object
    """
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            logger.exception(f"Database session error: {e}")
            session.rollback()
            raise
        finally:
            session.close()


@contextmanager
def session_manager() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    This context manager provides a database session that is automatically
    committed or rolled back based on whether an exception is raised.
    
    Yields:
        SQLModel Session object
    """
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception as e:
            logger.exception(f"Database error: {e}")
            session.rollback()
            raise
        finally:
            session.close()


class BaseRepository:
    """
    Base repository for database operations.
    
    This class provides a base implementation of common database operations
    that can be inherited by module-specific repositories.
    """
    
    def __init__(self, session: Session):
        """
        Initialize the repository with a database session.
        
        Args:
            session: SQLModel Session object
        """
        self.session = session
    
    def get(self, model: Type[ModelType], id: Any) -> ModelType | None:
        """
        Get a model instance by ID.
        
        Args:
            model: SQLModel model class
            id: Primary key value
            
        Returns:
            Model instance if found, None otherwise
        """
        return self.session.get(model, id)
    
    def get_multi(
        self, 
        model: Type[ModelType], 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> list[ModelType]:
        """
        Get multiple model instances with pagination.
        
        Args:
            model: SQLModel model class
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of model instances
        """
        statement = select(model).offset(skip).limit(limit)
        return list(self.session.exec(statement))
    
    def create(self, model_instance: ModelType) -> ModelType:
        """
        Create a new record in the database.
        
        Args:
            model_instance: Instance of a SQLModel model
            
        Returns:
            Created model instance with ID populated
        """
        self.session.add(model_instance)
        self.session.commit()
        self.session.refresh(model_instance)
        return model_instance
    
    def update(self, model_instance: ModelType) -> ModelType:
        """
        Update an existing record in the database.
        
        Args:
            model_instance: Instance of a SQLModel model
            
        Returns:
            Updated model instance
        """
        self.session.add(model_instance)
        self.session.commit()
        self.session.refresh(model_instance)
        return model_instance
    
    def delete(self, model_instance: ModelType) -> None:
        """
        Delete a record from the database.
        
        Args:
            model_instance: Instance of a SQLModel model
        """
        self.session.delete(model_instance)
        self.session.commit()


# Dependency to inject a repository into a route
def get_repository(repo_class: Type[T]) -> Callable[[Session], T]:
    """
    Factory function for repository injection.
    
    This function creates a dependency that injects a repository instance
    into a route function.
    
    Args:
        repo_class: Repository class to instantiate
        
    Returns:
        Dependency function
    """
    def _get_repo(session: Session = Depends(get_session)) -> T:
        return repo_class(session)
    return _get_repo


# Reusable dependency for a database session
SessionDep = Depends(get_session)


def init_db(session: Session) -> None:
    """
    Initialize database with required data.
    
    During the modular transition, we're delegating this to the users module
    to create the initial superuser. In the future, this will be a coordinated
    initialization process for all modules.
    
    Args:
        session: Database session
    """
    # Import here to avoid circular imports
    from app.modules.users.repository.user_repo import UserRepository
    from app.modules.users.services.user_service import UserService
    
    # Initialize user data (create superuser)
    user_repo = UserRepository(session)
    user_service = UserService(user_repo)
    user_service.create_initial_superuser()
    
    logger.info("Database initialized with initial data")