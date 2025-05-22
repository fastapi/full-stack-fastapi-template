"""
Database utilities for testing.
"""
import uuid
from datetime import datetime
from typing import Dict, List, Type, Any, Optional

from sqlmodel import Session, SQLModel, select

from app.models import User, Item, WorkoutPost, UserFollow, Workout, Exercise
from app.models.user import UserCreate
from app.crud import create_user


def create_test_db_and_tables(engine):
    """Create all tables in the test database."""
    SQLModel.metadata.create_all(engine)


def clear_test_db(db: Session):
    """Clear all data from the test database."""
    for model in [Exercise, Workout, WorkoutPost, UserFollow, Item, User]:
        db.exec(f"DELETE FROM {model.__tablename__}")
    db.commit()


def create_test_user(
    db: Session, 
    email: str = "test@example.com", 
    password: str = "testpassword", 
    is_superuser: bool = False,
    full_name: Optional[str] = "Test User"
) -> User:
    """Create a test user in the database."""
    user_in = UserCreate(
        email=email,
        password=password,
        is_superuser=is_superuser,
        full_name=full_name,
    )
    return create_user(session=db, user_create=user_in)


def create_test_workout_post(
    db: Session, 
    user_id: str, 
    title: str = "Test Workout", 
    workout_type: str = "Running",
    duration_minutes: int = 30,
    calories_burned: Optional[int] = 300,
    description: Optional[str] = "Test workout description"
) -> WorkoutPost:
    """Create a test workout post in the database."""
    from app.models.social import WorkoutPost
    
    workout_post = WorkoutPost(
        user_id=user_id,
        title=title,
        workout_type=workout_type,
        duration_minutes=duration_minutes,
        calories_burned=calories_burned,
        description=description
    )
    db.add(workout_post)
    db.commit()
    db.refresh(workout_post)
    return workout_post


def create_test_follow_relationship(
    db: Session, 
    follower_id: str, 
    followed_id: str
) -> UserFollow:
    """Create a test follow relationship in the database."""
    follow = UserFollow(
        follower_id=follower_id,
        followed_id=followed_id
    )
    db.add(follow)
    db.commit()
    db.refresh(follow)
    return follow


def get_test_object_count(db: Session, model: Type[SQLModel]) -> int:
    """Get the count of objects of a specific model in the test database."""
    return db.exec(select(model)).count()


def create_test_workout(
    db: Session,
    user_id: uuid.UUID,
    name: str = "Test Workout",
    description: Optional[str] = "Test workout description",
    scheduled_date: Optional[datetime] = None,
    duration_minutes: Optional[int] = 60,
    is_completed: bool = False
) -> Workout:
    """Create a test workout in the database."""
    workout = Workout(
        user_id=user_id,
        name=name,
        description=description,
        scheduled_date=scheduled_date,
        duration_minutes=duration_minutes,
        is_completed=is_completed
    )
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout


def create_test_exercise(
    db: Session,
    workout_id: uuid.UUID,
    name: str = "Test Exercise",
    category: str = "Strength",
    description: Optional[str] = "Test exercise description",
    sets: Optional[int] = 3,
    reps: Optional[int] = 10,
    weight: Optional[float] = 50.0
) -> Exercise:
    """Create a test exercise in the database."""
    exercise = Exercise(
        workout_id=workout_id,
        name=name,
        description=description,
        category=category,
        sets=sets,
        reps=reps,
        weight=weight
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise