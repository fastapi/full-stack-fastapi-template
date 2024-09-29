from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
import uuid
from typing import Optional
from pydantic import EmailStr

class TokenBlacklist(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    jti: str = Field(index=True, unique=True)  # Store JWT ID (jti)
    user_id: uuid.UUID = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

class OtplessPhoneAuthDetails(SQLModel):
    mode: str
    phone_number: str
    country_code: str
    auth_state: str

class OtplessEmailAuthDetails(SQLModel):
    email: EmailStr
    mode: str
    auth_state: str

class AuthenticationDetails(SQLModel):
    phone: OtplessPhoneAuthDetails
    email: OtplessEmailAuthDetails

class OtplessVerifyTokenResponse(SQLModel):
    name: str
    email: EmailStr
    first_name: str
    last_name: str
    family_name: str
    phone_number: str
    national_phone_number: str
    country_code: str
    email_verified: bool
    auth_time: str
    authentication_details: AuthenticationDetails

class OtplessToken(SQLModel):
    otpless_token: str

class TokenModel(SQLModel):
    sub: str  
    exp: Optional[int] = None  

class RefreshTokenPayload(SQLModel):
    refresh_token: str

class AccessToken(SQLModel):
    token: str
    expires_at: datetime
    token_type: str = "Bearer"

class RefreshToken(SQLModel):
    token: str
    expires_at: datetime

class UserAuthResponse(SQLModel):
    access_token: AccessToken
    refresh_token: RefreshToken
    issued_at: datetime
    