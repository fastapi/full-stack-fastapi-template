from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app import crud
from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User

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


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


# Role-based permission checking
def require_role(required_role: str):
    """Dependency factory to require a specific role."""
    def check_role(current_user: CurrentUser) -> User:
        if not crud.user_has_role(current_user, required_role) and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have required role: {required_role}"
            )
        return current_user
    return check_role


def require_any_role(required_roles: list[str]):
    """Dependency factory to require any of the specified roles."""
    def check_roles(current_user: CurrentUser) -> User:
        if not crud.user_has_any_role(current_user, required_roles) and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have any of the required roles: {', '.join(required_roles)}"
            )
        return current_user
    return check_roles


# Predefined role dependencies for common use cases
AdminUser = Annotated[User, Depends(require_role("admin"))]
RunnerUser = Annotated[User, Depends(require_role("runner"))]
OrganizerUser = Annotated[User, Depends(require_role("organizer"))]
VolunteerUser = Annotated[User, Depends(require_role("volunteer"))]

# Combined role dependencies
AdminOrOrganizerUser = Annotated[User, Depends(require_any_role(["admin", "organizer"]))]
