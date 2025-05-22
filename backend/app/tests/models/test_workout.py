"""
Tests for workout models.
"""
import uuid
from datetime import datetime, timedelta

import pytest
from sqlmodel import Session

from app.models import User, Workout, Exercise
from app.tests.utils.test_db import (
    create_test_user,
    create_test_workout,
    create_test_exercise,
)


def test_create_workout(db: Session):
    """Test creating a workout."""
    # Create a test user
    user = create_test_user(db)
    
    # Create a workout
    workout_name = "Monday Strength Training"
    workout_description = "Focus on upper body"
    scheduled_date = datetime.utcnow() + timedelta(days=1)
    
    workout = create_test_workout(
        db=db,
        user_id=user.id,
        name=workout_name,
        description=workout_description,
        scheduled_date=scheduled_date,
        duration_minutes=45,
    )
    
    # Check that the workout was created correctly
    assert workout.id is not None
    assert workout.user_id == user.id
    assert workout.name == workout_name
    assert workout.description == workout_description
    assert workout.scheduled_date == scheduled_date
    assert workout.duration_minutes == 45
    assert workout.is_completed is False
    assert workout.created_at is not None
    assert workout.updated_at is None


def test_create_exercise(db: Session):
    """Test creating an exercise for a workout."""
    # Create a test user and workout
    user = create_test_user(db)
    workout = create_test_workout(db=db, user_id=user.id)
    
    # Create an exercise
    exercise_name = "Bench Press"
    exercise_category = "Strength"
    exercise_description = "Flat bench press with barbell"
    
    exercise = create_test_exercise(
        db=db,
        workout_id=workout.id,
        name=exercise_name,
        category=exercise_category,
        description=exercise_description,
        sets=4,
        reps=8,
        weight=135.5,
    )
    
    # Check that the exercise was created correctly
    assert exercise.id is not None
    assert exercise.workout_id == workout.id
    assert exercise.name == exercise_name
    assert exercise.category == exercise_category
    assert exercise.description == exercise_description
    assert exercise.sets == 4
    assert exercise.reps == 8
    assert exercise.weight == 135.5
    assert exercise.created_at is not None
    assert exercise.updated_at is None


def test_workout_user_relationship(db: Session):
    """Test the relationship between workout and user."""
    # Create a test user
    user = create_test_user(db)
    
    # Create a workout
    workout = create_test_workout(db=db, user_id=user.id)
    
    # Check that the relationship works
    assert workout.user.id == user.id
    assert workout in user.workouts


def test_workout_exercise_relationship(db: Session):
    """Test the relationship between workout and exercises."""
    # Create a test user and workout
    user = create_test_user(db)
    workout = create_test_workout(db=db, user_id=user.id)
    
    # Create exercises
    exercise1 = create_test_exercise(
        db=db, workout_id=workout.id, name="Squats", category="Legs"
    )
    exercise2 = create_test_exercise(
        db=db, workout_id=workout.id, name="Deadlifts", category="Back"
    )
    
    # Check that the relationship works
    assert exercise1 in workout.exercises
    assert exercise2 in workout.exercises
    assert len(workout.exercises) == 2
    assert exercise1.workout.id == workout.id
    assert exercise2.workout.id == workout.id


def test_cascade_delete(db: Session):
    """Test that deleting a workout cascades to exercises."""
    # Create a test user and workout
    user = create_test_user(db)
    workout = create_test_workout(db=db, user_id=user.id)
    
    # Create exercises
    exercise1 = create_test_exercise(db=db, workout_id=workout.id)
    exercise2 = create_test_exercise(db=db, workout_id=workout.id)
    
    # Delete the workout
    db.delete(workout)
    db.commit()
    
    # Check that the exercises were also deleted
    exercises = db.query(Exercise).all()
    assert len(exercises) == 0
    
    # Create a new workout for the user
    workout = create_test_workout(db=db, user_id=user.id)
    exercise = create_test_exercise(db=db, workout_id=workout.id)
    
    # Delete the user
    db.delete(user)
    db.commit()
    
    # Check that the workout and exercise were also deleted
    workouts = db.query(Workout).all()
    exercises = db.query(Exercise).all()
    assert len(workouts) == 0
    assert len(exercises) == 0