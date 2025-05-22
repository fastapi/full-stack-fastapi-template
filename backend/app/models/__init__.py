from sqlmodel import SQLModel  # Re-export SQLModel for Alembic

from app.models.token import Message, NewPassword, Token, TokenPayload
from app.models.user import (
    UpdatePassword,
    User,
    UserBase,
    UserCreate,
    UserPublic,
    UserPublicExtended,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.models.item import (
    Item,
    ItemBase,
    ItemCreate,
    ItemPublic,
    ItemsPublic,
    ItemUpdate,
)
from app.models.social import (
    UserFollow,
    WorkoutPost,
    WorkoutPostCreate,
    WorkoutPostPublic,
    WorkoutPostsPublic,
    WorkoutPostUpdate,
)
from app.models.workout import (
    Workout,
    Exercise,
    WorkoutCreate,
    WorkoutUpdate,
    ExerciseCreate,
    ExerciseUpdate,
    WorkoutPublic,
    ExercisePublic,
    WorkoutWithExercisesPublic,
    WorkoutsPublic,
)

__all__ = [
    # SQLModel
    "SQLModel",
    # User models
    "User",
    "UserBase",
    "UserCreate",
    "UserPublic",
    "UserPublicExtended",
    "UserRegister",
    "UsersPublic",
    "UserUpdate",
    "UserUpdateMe",
    "UpdatePassword",
    
    # Item models
    "Item",
    "ItemBase",
    "ItemCreate",
    "ItemPublic",
    "ItemsPublic",
    "ItemUpdate",
    
    # Token models
    "Token",
    "TokenPayload",
    "NewPassword",
    "Message",
    
    # Social models
    "UserFollow",
    "WorkoutPost",
    "WorkoutPostCreate",
    "WorkoutPostPublic",
    "WorkoutPostsPublic",
    "WorkoutPostUpdate",
    
    # Workout models
    "Workout",
    "Exercise",
    "WorkoutCreate",
    "WorkoutUpdate",
    "ExerciseCreate",
    "ExerciseUpdate",
    "WorkoutPublic",
    "ExercisePublic",
    "WorkoutWithExercisesPublic",
    "WorkoutsPublic",
]