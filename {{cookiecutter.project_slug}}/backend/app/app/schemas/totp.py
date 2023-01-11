from typing import Optional
from pydantic import BaseModel


class NewTOTP(BaseModel):
    secret: Optional[str] = None
    key: str
    uri: str


class EnableTOTP(BaseModel):
    claim: str
    uri: str
    password: Optional[str] = None
