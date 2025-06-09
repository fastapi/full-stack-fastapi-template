import uuid
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

# Import directly from user module to avoid circular imports
from app.models.user import User

# Workout Model
class Workout(SQLModel, table=True):
    """
    Model representing a workout plan.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    scheduled_date: Optional[datetime] = Field(default=None)
    completed_date: Optional[datetime] = Field(default=None)
    duration_minutes: Optional[int] = Field(default=None, ge=0)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    user: User = Relationship(back_populates="workouts")
    exercises: List["Exercise"] = Relationship(back_populates="workout", cascade_delete=True)


# Exercise Model
class Exercise(SQLModel, table=True):
    """
    Model representing an exercise within a workout.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    workout_id: uuid.UUID = Field(foreign_key="workout.id", nullable=False)
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    category: str = Field(max_length=50)
    sets: Optional[int] = Field(default=None, ge=0)
    reps: Optional[int] = Field(default=None, ge=0)
    weight: Optional[float] = Field(default=None, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    workout: Workout = Relationship(back_populates="exercises")


# Exercise Create Schema
class ExerciseCreate(SQLModel):
    """
    Schema for creating an exercise.
    """
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    category: str = Field(max_length=50)
    sets: Optional[int] = Field(default=None, ge=0)
    reps: Optional[int] = Field(default=None, ge=0)
    weight: Optional[float] = Field(default=None, ge=0)


# Exercise Update Schema
class ExerciseUpdate(SQLModel):
    """
    Schema for updating an exercise.
    """
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    category: Optional[str] = Field(default=None, max_length=50)
    sets: Optional[int] = Field(default=None, ge=0)
    reps: Optional[int] = Field(default=None, ge=0)
    weight: Optional[float] = Field(default=None, ge=0)


# Workout Create Schema
class WorkoutCreate(SQLModel):
    """
    Schema for creating a workout.
    """
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    scheduled_date: Optional[datetime] = Field(default=None)
    duration_minutes: Optional[int] = Field(default=None, ge=0)
    exercises: List[ExerciseCreate] = [] 


# Workout Update Schema
class WorkoutUpdate(SQLModel):
    """
    Schema for updating a workout.
    """
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    scheduled_date: Optional[datetime] = Field(default=None)
    completed_date: Optional[datetime] = Field(default=None)
    duration_minutes: Optional[int] = Field(default=None, ge=0)
    is_completed: Optional[bool] = Field(default=None)

# Workout Public Schema
class WorkoutPublic(SQLModel):
    """
    Schema for returning workout data via API.
    """
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    exercise_count: Optional[int] = None


# Exercise Public Schema
class ExercisePublic(SQLModel):
    """
    Schema for returning exercise data via API.
    """
    id: uuid.UUID
    workout_id: uuid.UUID
    name: str
    description: Optional[str] = None
    category: str
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

#Workout with Exercise Public Schema
class WorkoutWithExercisesPublic(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    exercises: List[ExercisePublic] = []

#Personal Bests Model - Related to Workouts
class PersonalBest(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    exercise_name: str
    metric_type: str  # e.g. "max_weight", "max_reps"
    metric_value: float
    date_achieved: Optional[datetime]

class PersonalBestCreate(SQLModel):
    exercise_name: str
    metric_type: str
    metric_value: float
    date_achieved: Optional[datetime]

class PersonalBestPublic(SQLModel):
    id: UUID
    user_id: UUID
    exercise_name: str
    metric_type: str
    metric_value: float
    date_achieved: Optional[datetime]