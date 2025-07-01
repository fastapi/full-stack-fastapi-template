from typing import Optional, List
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from enum import Enum


security = HTTPBearer()


class UserRole(str, Enum):
    """Enumeración de roles de usuario"""
    CEO = "ceo"
    MANAGER = "manager"
    SUPERVISOR = "supervisor"
    HR = "hr"
    SUPPORT = "support"
    AGENT = "agent"
    CLIENT = "client"
    USER = "user"


async def verify_clerk_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verificar token de Clerk"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado"
        )
    
    # TODO: Implementar verificación real con Clerk
    # Por ahora retornamos un usuario mock
    return {
        "id": "user_123",
        "email": "user@example.com",
        "role": "agent",
        "metadata": {}
    }


def require_role(required_roles: List[str]):
    """Decorador para requerir roles específicos"""
    async def role_checker(user: dict = Depends(verify_clerk_token)) -> dict:
        if user.get("role") not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes"
            )
        return user
    return role_checker


def role_required(required_roles: List[str]):
    """Alias para require_role para compatibilidad"""
    return require_role(required_roles)


# Funciones específicas para cada rol
def ceo_role():
    return require_role(["ceo"])

def manager_role():
    return require_role(["ceo", "manager"])

def supervisor_role():
    return require_role(["ceo", "manager", "supervisor"])

def hr_role():
    return require_role(["ceo", "hr"])

def support_role():
    return require_role(["ceo", "support"])

def agent_role():
    return require_role(["ceo", "manager", "supervisor", "agent"])