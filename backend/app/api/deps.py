import logging
from collections.abc import Callable, Generator
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
from app.core.permissions import Permission, user_has_permission
from app.models import TokenPayload, User, UserRole

logger = logging.getLogger(__name__)

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session]:
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
    except InvalidTokenError, ValidationError:
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


def _log_access_denied(
    user: User,
    *,
    permission: Permission | None = None,
    required_roles: tuple[UserRole, ...] | None = None,
) -> None:
    if permission is not None:
        logger.warning(
            "Access denied: user_id=%s email=%s role=%s permission=%s",
            user.id,
            user.email,
            user.role.value,
            permission.value,
        )
    elif required_roles is not None:
        logger.warning(
            "Access denied: user_id=%s email=%s role=%s required_roles=%s",
            user.id,
            user.email,
            user.role.value,
            [role.value for role in required_roles],
        )


def require_permission(permission: Permission) -> Callable[..., User]:
    def permission_checker(current_user: CurrentUser) -> User:
        if not user_has_permission(current_user, permission):
            _log_access_denied(current_user, permission=permission)
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return permission_checker


def require_roles(*roles: UserRole) -> Callable[..., User]:
    allowed = set(roles)

    def role_checker(current_user: CurrentUser) -> User:
        if current_user.role not in allowed:
            _log_access_denied(current_user, required_roles=roles)
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_checker


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if current_user.role != UserRole.ADMIN:
        _log_access_denied(current_user, required_roles=(UserRole.ADMIN,))
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
