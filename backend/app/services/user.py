import uuid
from typing import Any, Optional

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """
    Create a new user in the database.
    
    Args:
        session: Database session
        user_create: User create schema
        
    Returns:
        Created user
    """
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> User:
    """
    Update a user in the database.
    
    Args:
        session: Database session
        db_user: Existing user object
        user_in: User update schema
        
    Returns:
        Updated user
    """
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> Optional[User]:
    """
    Get a user by email.
    
    Args:
        session: Database session
        email: User email
        
    Returns:
        User if found, None otherwise
    """
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user.
    
    Args:
        session: Database session
        email: User email
        password: User password
        
    Returns:
        User if authentication succeeded, None otherwise
    """
    user = get_user_by_email(session=session, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_user_by_id(*, session: Session, user_id: uuid.UUID) -> Optional[User]:
    """
    Get a user by ID.
    
    Args:
        session: Database session
        user_id: User ID
        
    Returns:
        User if found, None otherwise
    """
    statement = select(User).where(User.id == user_id)
    session_user = session.exec(statement).first()
    return session_user


def get_users(*, session: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """
    Get a list of users.
    
    Args:
        session: Database session
        skip: Number of users to skip
        limit: Maximum number of users to return
        
    Returns:
        List of users
    """
    statement = select(User).offset(skip).limit(limit)
    return list(session.exec(statement).all()) 