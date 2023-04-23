from typing import Optional, Dict, Any, List

from pydantic import BaseModel, validator

from app.models.role import Role
from app.schemas.role import RoleCreate


# Shared properties
class PermissionBase(BaseModel):
    id: int = None
    object: str = None
    permissions: Optional[Dict[str, str]] = None
    role: Optional[Any] = None

    @validator("role")
    def validate_role(cls, val):
        if issubclass(type(val), Role):
            return val

        raise TypeError("Wrong type for 'role', must be subclass of Role")


# Properties to receive on item creation
class PermissionCreate(PermissionBase):
    role_id: Optional[Any] = None
    object: str = None
    permissions: Optional[Dict[str, str]] = None

    class Config:
        arbitrary_types_allowed = True

    @validator("role_id")
    def validate_role_id(cls, val):
        print('Val:', val)
        print('Type:', type(val))
        if issubclass(type(val), Dict):
            return val

        raise TypeError("Wrong type for 'role', must be subclass of Role Create")


# Properties to receive on item update
class PermissionUpdate(PermissionCreate):
    pass


# Properties shared by models stored in DB
class PermissionInDBBase(PermissionBase):
    role_id: int = None
    object: str = None
    permissions: Optional[Dict[str, str]] = None

    class Config:
        orm_mode = True


# Properties to return to client
class Permission(PermissionInDBBase):
    pass


# Properties stored in DB
class PermissionInDB(PermissionInDBBase):
    pass
