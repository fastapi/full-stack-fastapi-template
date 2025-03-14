from typing import Any, Generic, TypeVar

from pydantic import BaseModel

# Generic message
class Message(BaseModel):
    message: str

# JSON payload containing access token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Contents of JWT token
class TokenPayload(BaseModel):
    sub: str | None = None

# Standard API response wrapper
T = TypeVar('T')
class StandardResponse(BaseModel, Generic[T]):
    data: T
    success: bool = True
    message: str | None = None

# Standard error response
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Any | None = None 