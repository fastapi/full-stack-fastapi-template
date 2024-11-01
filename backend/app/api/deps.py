from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from app.core.db import engine
from app.core.security import get_jwt_payload
from app.models.user import UserBusiness, UserPublic

# OAuth2PasswordBearer to extract the token from the request header
bearer_scheme = HTTPBearer()

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]

# Dependency to get the current user
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    session: SessionDep
) -> UserPublic | UserBusiness:
    # print('credentials.credentials ', credentials.credentials)
    try:
        print('credentials.credentials ', credentials.credentials)
        # Verify and decode the token (ensure this is as fast as possible)
        token_data = get_jwt_payload(credentials.credentials)
        user_id = token_data.sub
        print('hhuuuser_id ',    user_id)
        # Query both user types in a single call, using a union if possible
        user = (
            session.query(UserPublic)
            .filter(UserPublic.id == user_id)
            .first()
        ) or (
            session.query(UserBusiness)
            .filter(UserBusiness.id == user_id)
            .first()
        )

        # If no user is found or the user is inactive, raise an error
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )

        return user

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# Dependency to get the business user
async def get_business_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    session: SessionDep
) -> UserBusiness:
    current_user = await get_current_user(credentials, session)
    if not isinstance(current_user, UserBusiness):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a business user",
        )
    return current_user

# Dependency to get the superuser
async def get_super_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    session: SessionDep
) -> UserBusiness:
    current_user = await get_business_user(credentials, session)
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a superuser",
        )
    return current_user

# Dependency to get any public user
async def get_public_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    session: SessionDep
) -> UserPublic:
    print('credentials.credentials ', credentials.credentials)
    current_user = await get_current_user(credentials, session)
    # print('current_user ', current_user)
    if not isinstance(current_user, UserPublic):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a public user",
        )
    return current_user
