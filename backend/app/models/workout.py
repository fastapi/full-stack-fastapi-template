import uuid
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy.orm import relationship

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
    exercises: List["WorkoutExercise"] = Relationship(back_populates="workout")


# Exercise Model Old


#New Exercise Model

class WorkoutExercise(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid4, primary_key=True)
    workout_id: uuid.UUID = Field(foreign_key="workout.id")
    name: str  # Or use foreign key to a static ExerciseCatalog table if needed
    muscle_group: Optional[str] = None
    type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    workout: "Workout" = Relationship(back_populates="exercises")
    sets: List["WorkoutSet"] = Relationship(back_populates="exercise")


class WorkoutSet(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid4, primary_key=True)
    exercise_id: uuid.UUID = Field(foreign_key="workoutexercise.id")
    weight: float
    reps: int

    exercise: "WorkoutExercise" = Relationship(back_populates="sets")

class WorkoutSetCreate(SQLModel):
    weight: float
    reps: int


class WorkoutExerciseCreate(SQLModel):
    name: str
    muscle_group: Optional[str]
    type: Optional[str]
    sets: List[WorkoutSetCreate]

class WorkoutSetPublic(SQLModel):
    id: uuid.UUID
    weight: float
    reps: int

class WorkoutExercisePublic(SQLModel):
    id: uuid.UUID
    name: str
    muscle_group: Optional[str] = None
    type: Optional[str] = None
    sets: List[WorkoutSetPublic] = []
    created_at: datetime

class WorkoutSetUpdate(SQLModel):
    id: Optional[uuid.UUID]
    weight: float
    reps: int

class WorkoutExerciseUpdate(SQLModel):
    id: Optional[uuid.UUID]
    name: str
    muscle_group: Optional[str]
    type: Optional[str]
    sets: List[WorkoutSetUpdate]

# Workout Create Schema

class WorkoutCreate(SQLModel):
    name: str
    description: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    is_completed: bool = False
    completed_date: Optional[datetime] = None
    exercises: List[WorkoutExerciseCreate]


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
    exercises: Optional[List[WorkoutExerciseUpdate]] = None



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

# Workout With Exercises Public Schema
class WorkoutWithExercisesPublic(WorkoutPublic):
    """
    Schema for returning workout data with exercises via API.
    """
    exercises: List[WorkoutExercisePublic] = []


# Workouts Public Schema
class WorkoutsPublic(SQLModel):
    """
    Schema for returning multiple workouts via API.
    """
    data: List[WorkoutPublic]
    count: int

