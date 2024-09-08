import random
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from .user import UserPublic, UserUpdateMe


class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserPublic


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: UUID
    exp: datetime
    type: str 


class NewPassword(SQLModel):
    token: str
    new_password: str

class OauthTokenBase(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    access_token: str = Field()
    refresh_token: str = Field()
    user_id: UUID = Field(foreign_key="user.id", unique=True)
    expires_at: datetime  | None = Field(default=None)


class UserOAuthToken(OauthTokenBase, table=True):
    __tablename__:str = "user_oauthtoken"
    user: "User" = Relationship(back_populates="user_oauth_token")

class OTPOAuth(SQLModel, table=True):
    __tablename__:str = 'otp_auth'
    id: int = Field(primary_key=True, default=None)
    user_id: UUID = Field(foreign_key="user.id")
    token: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    def is_active(self):
        # Get the current UTC time
        current_time = datetime.utcnow()
        # Calculate the time difference
        time_diff = current_time - self.created_at
        # Check if the difference is less than or equal to 2 minutes
        return time_diff <= timedelta(minutes=5)

class OTPOAuthCreate(SQLModel):
    user_id: UUID
    token: str = Field(default_factory=lambda: f"{random.randint(0, 999999):06d}")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OTPOAuthVerify(SQLModel):
    user_id: UUID
    primary_email: str
    token: str


class OAuthRegisterPayload(SQLModel):
    accessToken: str
    refreshToken: str
    expires: str
    user: UserUpdateMe
    def convert_date(self) -> datetime:
        return datetime.fromisoformat(self.expires.replace('Z', '+00:00'))

class OtpResend(SQLModel):
    user_id: UUID
    primary_email: str

class RecoverPassword(SQLModel):
    email: str