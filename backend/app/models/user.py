from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from pydantic import validator
from typing import Optional, List


# Shared properties for database models
class UserBase(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    primary_email: str = Field(unique=True, index=True)
    secondary_email: str | None = Field(unique=True, index=True, default=None)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    full_name: str | None = None
    oauth: str | None = Field(default=None)
    email_verified_primary: bool = Field(default=False)
    email_verified_secondary: bool = Field(default=False)
    onboarded: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    hashed_password: str

    @validator("full_name")
    def validate_full_name(cls, v):
        if v and len(v) < 3:
            raise ValueError("Full name must be at least 3 characters long")
        return v

    @validator("oauth")
    def validate_oauth(cls, v):
        if v and not v.startswith("oauth_"):
            raise ValueError("OAuth must start with 'oauth_'")
        return v

# Database model, table is inferred from class name
class User(UserBase, table=True):
    user_oauth_token: "UserOAuthToken" = Relationship(back_populates="user")
    resumes: list["UserResumes"] = Relationship(back_populates="user")
    resumes_json: "UserResumeJson" = Relationship(back_populates="user")



# Properties to receive via API on creation
class UserCreate(SQLModel):
    primary_email: str
    password: str
    full_name: str | None = None
    secondary_email: str | None = None



class UserRegister(SQLModel):
    primary_email: str
    password: str
    full_name: str | None = None


# Properties to receive via API on update
class UserUpdate(SQLModel):
    primary_email: str | None = None
    secondary_email: str | None = None
    password: str | None = None
    full_name: str | None = None
    is_active: Optional[bool] = False
    is_superuser: Optional[bool] = False
    email_verified_primary: Optional[bool] = False


# Specific properties for updating the user's own profile
class UserUpdateMe(SQLModel):
    full_name: str
    primary_email: str


# Properties for updating passwords
class UpdatePassword(SQLModel):
    current_password: str
    new_password: str


# Properties to return via API, id is always required
class UserPublic(SQLModel):
    id: UUID
    primary_email: str
    full_name: str | None = None
    is_active: bool
    is_superuser: bool
    email_verified_primary: bool
    onboarded: bool


# Wrapper for a list of public users
class UsersPublic(SQLModel):
    data: List[UserPublic]
    count: int
