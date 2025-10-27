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
from app.models import TokenPayload, User, UserRole

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


# ============================================================================
# INVENTORY MANAGEMENT SYSTEM - ROLE-BASED PERMISSIONS
# ============================================================================


def require_role(allowed_roles: list[UserRole]):
    """
    Decorator factory for role-based access control.
    Usage: dependencies=[Depends(require_role([UserRole.ADMINISTRADOR]))]
    """
    def role_checker(current_user: CurrentUser) -> User:
        if current_user.is_superuser:
            # Superusers have access to everything
            return current_user

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user

    return role_checker


# Convenience dependencies for common role combinations
def get_administrador_user(current_user: CurrentUser) -> User:
    """Only administrador can access"""
    if not current_user.is_superuser and current_user.role != UserRole.ADMINISTRADOR:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Administrador role required."
        )
    return current_user


def get_administrador_or_auxiliar(current_user: CurrentUser) -> User:
    """Administrador or auxiliar can access (for inventory operations)"""
    if not current_user.is_superuser and current_user.role not in [
        UserRole.ADMINISTRADOR,
        UserRole.AUXILIAR
    ]:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Administrador or Auxiliar role required."
        )
    return current_user


def get_administrador_or_vendedor(current_user: CurrentUser) -> User:
    """Administrador or vendedor can access (for sales operations)"""
    if not current_user.is_superuser and current_user.role not in [
        UserRole.ADMINISTRADOR,
        UserRole.VENDEDOR
    ]:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Administrador or Vendedor role required."
        )
    return current_user


# Type aliases for convenience
AdministradorUser = Annotated[User, Depends(get_administrador_user)]
AdministradorOrAuxiliarUser = Annotated[User, Depends(get_administrador_or_auxiliar)]
AdministradorOrVendedorUser = Annotated[User, Depends(get_administrador_or_vendedor)]
