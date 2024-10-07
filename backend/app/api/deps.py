from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User

# Define OAuth2 scheme for token authentication
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    """
    Get a database session.

    This function creates a new session for the database and yields it.
    The session is automatically closed after the function is executed.
    It's not protected and can be used by any part of the application.

    Args:
        None

    Returns:
        Generator[Session, None, None]: A generator that yields the database session.

    Raises:
        None

    Notes:
        This function uses a context manager to ensure proper closure of the session.
    """
    with Session(engine) as session:
        yield session


# Define dependencies for database session and token
SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


# Function to get the current user from the token
def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """
    Get the current user from the token.

    This function decodes the JWT token and retrieves the corresponding user from the database.
    It's protected and used as a dependency in routes that require authentication.

    Args:
        session (SessionDep): The database session.
        token (TokenDep): The JWT token.

    Returns:
        User: The current authenticated user.

    Raises:
        HTTPException:
            - 403: If the token is invalid or expired.
            - 404: If the user is not found in the database.
            - 400: If the user account is inactive.

    Notes:
        This function performs token validation and user authentication.
    """
    try:
        # Decode the JWT token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        # Raise exception if token is invalid
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    # Get the user from the database
    user = session.get(User, token_data.sub)
    if not user:
        # Raise exception if user not found
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        # Raise exception if user is inactive
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


# Define dependency for getting the current user
CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    """
    Get the current active superuser.

    This function checks if the current user is a superuser.
    It's protected and used as a dependency in routes that require superuser privileges.

    Args:
        current_user (CurrentUser): The current authenticated user.

    Returns:
        User: The current active superuser.

    Raises:
        HTTPException:
            - 403: If the user is not a superuser.

    Notes:
        This function is typically used to restrict access to administrative endpoints.
    """
    if not current_user.is_superuser:
        # Raise exception if user is not a superuser
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
