from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.core.db import engine
from app.core.clerk_auth import get_current_user as clerk_get_current_user


def get_db() -> Generator[Session, None, None]:
    """Generar sesión de base de datos"""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]

# Usar la función de Clerk para obtener el usuario actual
def get_current_user() -> dict:
    """Obtener el usuario actual desde Clerk JWT"""
    return clerk_get_current_user()

CurrentUser = Annotated[dict, Depends(get_current_user)]
