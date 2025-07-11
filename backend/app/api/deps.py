from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import Request

from app.core.db import engine
from app.core.clerk_auth import get_current_user as clerk_get_current_user, security
from app.models import User


def get_db() -> Generator[Session, None, None]:
    """Generar sesión de base de datos"""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]

# Usar la función de Clerk para obtener el usuario actual
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: SessionDep = None
) -> User:
    """Obtener el usuario actual desde Clerk JWT y base de datos"""
    clerk_user = clerk_get_current_user(credentials)
    user_id = clerk_user.get("sub") or clerk_user.get("id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    # Buscar el usuario en la base de datos
    statement = select(User).where(User.clerk_id == user_id)
    user = session.exec(statement).first()
    
    if not user:
        # Si no existe, crear usuario básico desde Clerk
        user = User(
            clerk_id=user_id,
            email=clerk_user.get("email", ""),
            full_name=clerk_user.get("name", ""),
            hashed_password="",  # Usuario de Clerk, sin password local
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    
    return user


def get_current_active_superuser(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Verificar que el usuario actual sea superusuario activo"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


CurrentUser = Annotated[User, Depends(get_current_user)]
