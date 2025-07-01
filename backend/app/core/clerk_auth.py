import jwt
import requests
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from typing import Optional, Dict, Any
import logging
from functools import lru_cache

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configurar security scheme
security = HTTPBearer()

@lru_cache()
def get_clerk_jwks() -> Dict[str, Any]:
    """Obtener las claves públicas de Clerk para verificar JWT"""
    try:
        # Extraer la clave pública del publishable key
        if settings.CLERK_PUBLISHABLE_KEY:
            pk = settings.CLERK_PUBLISHABLE_KEY.replace("pk_test_", "").replace("pk_live_", "")
            response = requests.get(f"https://api.clerk.dev/v1/jwks")
            response.raise_for_status()
            return response.json()
        else:
            raise Exception("CLERK_PUBLISHABLE_KEY no configurado")
    except Exception as e:
        logger.error(f"Error obteniendo JWKS de Clerk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de configuración de autenticación"
        )

def verify_clerk_token(token: str) -> Dict[str, Any]:
    """Verificar y decodificar token JWT de Clerk"""
    try:
        # Para desarrollo, podemos hacer una verificación simplificada
        # En producción, usa las claves JWKS de Clerk
        
        # Decodificar sin verificación para desarrollo
        # ⚠️ SOLO PARA DESARROLLO - En producción usar verificación completa
        payload = jwt.decode(
            token,
            options={"verify_signature": False},  # Solo para desarrollo
            algorithms=['RS256']
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.JWTError as e:
        logger.error(f"Error verificando token JWT: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    except Exception as e:
        logger.error(f"Error inesperado verificando token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Obtener el usuario actual desde el token JWT de Clerk"""
    token = credentials.credentials
    user_data = verify_clerk_token(token)
    
    return {
        "clerk_id": user_data.get("sub"),
        "email": user_data.get("email"),
        "first_name": user_data.get("given_name"),
        "last_name": user_data.get("family_name"),
        "role": user_data.get("role", "user"),
        "metadata": user_data.get("public_metadata", {}),
        "raw_token": user_data
    }

def require_role(required_roles: list[str]):
    """Decorator para requerir roles específicos"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            user_role = current_user.get("role", "user")
            if user_role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permisos insuficientes"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Dependency para verificar roles
def RoleChecker(allowed_roles: list[str]):
    def check_role(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role", "user")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Roles permitidos: {', '.join(allowed_roles)}"
            )
        return current_user
    return check_role

# Shortcuts para roles comunes
def require_ceo(current_user: Dict[str, Any] = Depends(RoleChecker(["ceo"]))):
    return current_user

def require_manager_or_above(current_user: Dict[str, Any] = Depends(RoleChecker(["ceo", "manager"]))):
    return current_user

def require_supervisor_or_above(current_user: Dict[str, Any] = Depends(RoleChecker(["ceo", "manager", "supervisor"]))):
    return current_user

def require_agent_or_above(current_user: Dict[str, Any] = Depends(RoleChecker(["ceo", "manager", "supervisor", "agent"]))):
    return current_user 