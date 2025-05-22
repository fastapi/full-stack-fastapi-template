import uuid
from typing import List, Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: Optional[str] = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    password: Optional[str] = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[EmailStr] = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    
    # Relationships
    items: List["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    
    # Social relationships
    following: List["UserFollow"] = Relationship(
        back_populates="follower",
        sa_relationship_kwargs={"foreign_keys": "[UserFollow.follower_id]", "cascade": "all, delete-orphan"},
    )
    followers: List["UserFollow"] = Relationship(
        back_populates="followed",
        sa_relationship_kwargs={"foreign_keys": "[UserFollow.followed_id]", "cascade": "all, delete-orphan"},
    )
    
    # Workout posts
    workout_posts: List["WorkoutPost"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    
    # Workouts
    workouts: List["Workout"] = Relationship(
        back_populates="user", cascade_delete=True
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


# Extended user public model with follower counts
class UserPublicExtended(UserPublic):
    follower_count: int = 0
    following_count: int = 0


class UsersPublic(SQLModel):
    data: List[UserPublic]
    count: int


# Forward references for type hints
from app.models.social import UserFollow, WorkoutPost
from app.models.workout import Workout