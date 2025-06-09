from typing import List, Optional
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..config import settings
from ...models import User
from ...services.nhost import nhost_client

security = HTTPBearer()

class RoleMiddleware:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not current_user:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated"
            )
        
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role {current_user.role} not authorized for this endpoint"
            )
        
        return current_user

# Roles específicos
def ceo_role():
    return RoleMiddleware(["CEO"])

def manager_role():
    return RoleMiddleware(["CEO", "Gerente"])

def supervisor_role():
    return RoleMiddleware(["CEO", "Gerente", "Supervisor"])

def hr_role():
    return RoleMiddleware(["CEO", "RRHH"])

def support_role():
    return RoleMiddleware(["CEO", "Atención al Cliente"])

def agent_role():
    return RoleMiddleware(["CEO", "Gerente", "Supervisor", "Agente"])

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[User]:
    try:
        # Validar token con Nhost
        session = await nhost_client.auth.getSession()
        if not session:
            return None

        # Obtener usuario de la base de datos
        user = await nhost_client.graphql.query(
            """
            query GetUser($id: uuid!) {
                user(id: $id) {
                    id
                    email
                    role
                    metadata
                }
            }
            """,
            {"id": session.user.id}
        )

        if not user or not user.get("data", {}).get("user"):
            return None

        user_data = user["data"]["user"]
        return User(
            id=user_data["id"],
            email=user_data["email"],
            role=user_data["role"],
            metadata=user_data.get("metadata", {})
        )

    except Exception as e:
        print(f"Error getting current user: {e}")
        return None 