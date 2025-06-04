from typing import Optional
from pydantic import BaseModel
from app.models.user import UserPublic
from sqlmodel import SQLModel


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: Optional[str] = None

class TokenWithUser(BaseModel):
    access_token: str
    user: UserPublic

class NewPassword(SQLModel):
    token: str
    new_password: str


# Generic message
class Message(SQLModel):
    message: str