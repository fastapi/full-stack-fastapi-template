from app.models.auth import TokenBlacklist
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from app.models.user import UserPublic, UserBusiness
from app.core.security import get_jwt_payload
from typing import Annotated, Generator, Optional, Union
from app.core.config import settings
from app.core.db import engine

# OAuth2PasswordBearer to extract the token from the request header
bearer_scheme = HTTPBearer()

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]

# # Check if the token is blacklisted (optional)
# def is_token_blacklisted(session: Session, user_id: str, provided_token: str) -> bool:
#     """
#     Checks if the provided token is blacklisted by comparing it with the one stored in the user record.
    
#     Args:
#         session (Session): SQLAlchemy session to query the database.
#         user_id (str): The ID of the user.
#         provided_token (str): The provided refresh token to check.
        
#     Returns:
#         bool: True if the token is blacklisted (invalid), False otherwise.
#     """
#     # Fetch the user from the database using the user_id
#     user = session.query(UserPublic).filter(UserPublic.id == user_id).first()

#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Check if the provided token matches the stored refresh token
#     if user.refresh_token != provided_token:
#         # The token does not match, consider it invalid or blacklisted
#         return True

#     # If the token matches, it's not blacklisted
#     return False

# Dependency to get the current user
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    session: SessionDep
) -> Union[UserPublic, UserBusiness]:
    try:
        # Verify and decode the token (ensure this is as fast as possible)
        token_data = get_jwt_payload(credentials.credentials)
        user_id = token_data.sub

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
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), 
    session: Session = Depends(SessionDep)
) -> UserBusiness:
    current_user = await get_current_user(credentials.credentials, session)
    if not isinstance(current_user, UserBusiness):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a business user",
        )
    return current_user

# Dependency to get the superuser
async def get_super_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), 
    session: Session = Depends(SessionDep)
) -> UserPublic:
    current_user = await get_current_user(credentials, session)
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a superuser",
        )
    return current_user

# Dependency to get any public user
async def get_public_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), 
    session: Session = Depends(SessionDep)
) -> UserPublic:
    current_user = await get_current_user(credentials.credentials, session)
    if not isinstance(current_user, UserPublic):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a public user",
        )
    return current_user