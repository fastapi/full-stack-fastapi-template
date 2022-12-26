from pydantic import BaseModel, EmailStr
from typing import List


class EmailContent(BaseModel):
    email: EmailStr
    subject: str
    content: str


class EmailValidation(BaseModel):
    email: EmailStr
    subject: str
    token: str

