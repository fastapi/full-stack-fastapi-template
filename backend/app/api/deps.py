from collections.abc import Generator
from typing import Annotated
from enum import Enum

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session, select

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import Counselor, TokenPayload, User

class UserRole(str, Enum):
    USER = "user"
    TRAINER = "trainer"
    COUNSELOR = "counselor"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_user_role(user: User) -> UserRole:
    """Get user role based on current user data."""
    # Check explicit role field first
    if user.role:
        role_lower = user.role.lower()
        if role_lower in ["admin", "super_admin"] or user.is_superuser:
            return UserRole.ADMIN
        elif role_lower == "counselor":
            return UserRole.COUNSELOR
        elif role_lower == "trainer":
            return UserRole.TRAINER
        elif role_lower == "user":
            return UserRole.USER
    
    # Fallback to is_superuser for backwards compatibility
    if user.is_superuser:
        return UserRole.ADMIN
    
    return UserRole.USER


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


def get_current_active_user(current_user: CurrentUser) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Inactive user"
        )
    return current_user


def get_current_admin(current_user: CurrentUser) -> User:
    """Check if current user is an admin."""
    if get_user_role(current_user) != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )
    return current_user


def get_current_trainer_or_admin(current_user: CurrentUser) -> User:
    """Check if current user is a trainer or admin."""
    role = get_user_role(current_user)
    if role not in [UserRole.TRAINER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=403,
            detail="Trainer or admin privileges required"
        )
    return current_user


# Dependency annotations for common use cases
CurrentAdmin = Annotated[User, Depends(get_current_admin)]
CurrentTrainerOrAdmin = Annotated[User, Depends(get_current_trainer_or_admin)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]

async def get_current_counselor_or_admin(
    current_user: CurrentActiveUser,
    db: SessionDep,
) -> User:
    """
    Get current user if they are a counselor or admin.
    
    This function checks:
    1. If user has admin role or is_superuser -> allow access
    2. If user has counselor role -> check if counselor record exists
    3. If user has counselor record but no role -> update role and allow access
    """
    role = get_user_role(current_user)
    
    # Admin users always have access
    if role == UserRole.ADMIN or current_user.is_superuser:
        return current_user
    
    # Check if user has counselor role
    if role == UserRole.COUNSELOR:
        # Verify counselor record exists
        counselor = db.exec(
            select(Counselor).where(Counselor.user_id == current_user.id)
        ).first()
        
        if counselor:
            return current_user
        else:
            # User has counselor role but no counselor record
            raise HTTPException(
                status_code=403,
                detail="Counselor role detected but no counselor profile found. Please contact administrator."
            )
    
    # Check if user has counselor record but wrong role (legacy data)
    counselor = db.exec(
        select(Counselor).where(Counselor.user_id == current_user.id)
    ).first()
    
    if counselor:
        # User has counselor record but wrong role - fix it
        current_user.role = "counselor"
        db.add(current_user)
        db.commit()
        return current_user
    
    # User is neither admin nor counselor
    raise HTTPException(
        status_code=403,
        detail="Access denied. Counselor or administrator privileges required."
    )

CurrentCounselorOrAdmin = Annotated[User, Depends(get_current_counselor_or_admin)]
