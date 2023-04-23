from typing import Optional

from pydantic import BaseModel


# Shared properties
class RoleBase(BaseModel):
    name: str = None
    description: Optional[str] = None


# Properties to receive on item creation
class RoleCreate(RoleBase):
    name: str

    class Config:
        arbitrary_types_allowed = True


# Properties to receive on item update
class RoleUpdate(RoleBase):
    pass


# Properties shared by models stored in DB
class RoleInDBBase(RoleBase):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True


# Properties to return to client
class Role(RoleInDBBase):
    pass


# Properties properties stored in DB
class RoleInDB(RoleInDBBase):
    pass
