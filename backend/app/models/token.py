from typing import Optional

from sqlmodel import SQLModel


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: Optional[str] = None


class NewPassword(SQLModel):
    token: str
    new_password: str


# Generic message
class Message(SQLModel):
    message: str