import uuid
from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

# Import directly from user module to avoid circular imports
from app.models.user import User



# User Follow Relationship Model
class UserFollow(SQLModel, table=True):
    """
    Model representing a follow relationship between users.
    """
    follower_id: uuid.UUID = Field(
        foreign_key="user.id", primary_key=True, nullable=False
    )
    followed_id: uuid.UUID = Field(
        foreign_key="user.id", primary_key=True, nullable=False
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    follower: User = Relationship(
        back_populates="following",
        sa_relationship_kwargs={"foreign_keys": "[UserFollow.follower_id]"},
    )
    followed: User = Relationship(
        back_populates="followers",
        sa_relationship_kwargs={"foreign_keys": "[UserFollow.followed_id]"},
    )


# Workout/Activity Post Model
class WorkoutPost(SQLModel, table=True):
    """
    Model representing a workout or activity post.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    workout_type: str = Field(max_length=50)
    duration_minutes: int = Field(ge=1)
    calories_burned: Optional[int] = Field(default=None, ge=0)
    is_public: bool = Field(default=True)  # True for public posts, False for private posts
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    user: User = Relationship(back_populates="workout_posts")


# Workout Post Create Schema
class WorkoutPostCreate(SQLModel):
    """
    Schema for creating a workout post.
    """
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    workout_type: str = Field(max_length=50)
    duration_minutes: int = Field(ge=1)
    calories_burned: Optional[int] = Field(default=None, ge=0)
    is_public: bool = Field(default=True)  # Default to public posts


# Workout Post Update Schema
class WorkoutPostUpdate(SQLModel):
    """
    Schema for updating a workout post.
    """
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    workout_type: Optional[str] = Field(default=None, max_length=50)
    duration_minutes: Optional[int] = Field(default=None, ge=1)
    calories_burned: Optional[int] = Field(default=None, ge=0)
    is_public: Optional[bool] = Field(default=None)


# Workout Post Public Schema
class WorkoutPostPublic(SQLModel):
    """
    Schema for returning workout post data via API.
    """
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str] = None
    workout_type: str
    duration_minutes: int
    calories_burned: Optional[int] = None
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_full_name: Optional[str] = None  # Included for convenience in the feed
    is_mutual_follow: Optional[bool] = None  # For privacy logic in responses


# Workout Posts Public Schema
class WorkoutPostsPublic(SQLModel):
    """
    Schema for returning multiple workout posts via API.
    """
    data: List[WorkoutPostPublic]
    count: int


# User Search Result Schema
class UserSearchResult(SQLModel):
    """
    Schema for returning user search results with extended information.
    Extends UserPublicExtended with is_following status.
    """
    id: uuid.UUID
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    follower_count: int = 0
    following_count: int = 0
    is_following: bool = False


# User Search Results Public Schema
class UserSearchResultsPublic(SQLModel):
    """
    Schema for returning multiple user search results via API.
    """
    data: List[UserSearchResult]
    count: int