from collections.abc import Generator
from typing import Annotated, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session, select
from jose import JWTError
from datetime import datetime, timedelta

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User
from app.services.auth import AuthService
from app.services.property import PropertyService
from app.services.transactions import TransactionService
from app.services.analytics import AnalyticsService
from nhost import NhostClient
from ..services.credits import CreditService
from ..services.financial_analysis import FinancialAnalysisService

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_nhost_client() -> NhostClient:
    """Obtener el cliente de Nhost"""
    return NhostClient(
        subdomain=settings.NHOST_SUBDOMAIN,
        region=settings.NHOST_REGION
    )

def get_auth_service() -> AuthService:
    """Obtener el servicio de autenticación"""
    return AuthService(get_nhost_client())

def get_property_service() -> PropertyService:
    """Obtener el servicio de propiedades"""
    return PropertyService(get_nhost_client())

def get_transaction_service() -> TransactionService:
    """Obtener el servicio de transacciones"""
    return TransactionService(get_nhost_client())

def get_analytics_service() -> AnalyticsService:
    """Obtener el servicio de análisis"""
    return AnalyticsService(get_nhost_client())

def get_credit_service(nhost_client: NhostClient = Depends(get_nhost_client)) -> CreditService:
    return CreditService(nhost_client)

def get_financial_analysis_service(nhost_client: NhostClient = Depends(get_nhost_client)) -> FinancialAnalysisService:
    return FinancialAnalysisService(nhost_client)

async def get_current_user(
    token: str = Depends(reusable_oauth2),
    session: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Obtener el usuario actual basado en el token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Intentar obtener el usuario de la base de datos local primero
    user = session.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        # Si no está en la base de datos local, intentar obtenerlo de Nhost
        user = await auth_service.get_user_by_id(user_id)
        if user is None:
            raise credentials_exception
    
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verificar que el usuario actual está activo"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user

def get_current_verified_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Verificar que el usuario actual está verificado"""
    if not current_user.is_verified:
        raise HTTPException(status_code=400, detail="Usuario no verificado")
    return current_user

CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
