"""API dependency functions."""

from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app import constants
from app.core import config, db, security
from app.models import TokenPayload, User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{config.settings.API_V1_STR}/login/access-token",  # noqa: WPS237
)


def get_db() -> Generator[Session]:
    """Get database session."""
    with Session(db.engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def _validate_token(token: str) -> TokenPayload:
    """Validate JWT token and return payload."""
    try:
        payload = jwt.decode(
            token,
            config.settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from None
    try:
        return TokenPayload(**payload)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from None


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """Get current user from JWT token."""
    token_data = _validate_token(token)
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(
            status_code=constants.NOT_FOUND_CODE,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=constants.BAD_REQUEST_CODE,
            detail="Inactive user",
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    """Get current active superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=constants.FORBIDDEN_CODE,
            detail="The user doesn't have enough privileges",
        )
    return current_user
