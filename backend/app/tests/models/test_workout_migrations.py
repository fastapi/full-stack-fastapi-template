"""
Tests for workout model migrations.
"""
import pytest
from sqlalchemy import inspect
from sqlmodel import Session

from app.models import Workout, Exercise


def test_workout_table_exists(db: Session):
    """Test that the workout table exists with the correct columns."""
    # Get the inspector
    inspector = inspect(db.get_bind())
    
    # Check if the workout table exists
    assert "workout" in inspector.get_table_names()
    
    # Check if the workout table has the expected columns
    columns = {col["name"] for col in inspector.get_columns("workout")}
    expected_columns = {
        "id", "user_id", "name", "description", "scheduled_date", 
        "completed_date", "duration_minutes", "is_completed",
        "created_at", "updated_at"
    }
    assert expected_columns.issubset(columns)
    
    # Check foreign keys
    foreign_keys = inspector.get_foreign_keys("workout")
    assert any(fk["referred_table"] == "user" for fk in foreign_keys)


def test_exercise_table_exists(db: Session):
    """Test that the exercise table exists with the correct columns."""
    # Get the inspector
    inspector = inspect(db.get_bind())
    
    # Check if the exercise table exists
    assert "exercise" in inspector.get_table_names()
    
    # Check if the exercise table has the expected columns
    columns = {col["name"] for col in inspector.get_columns("exercise")}
    expected_columns = {
        "id", "workout_id", "name", "description", "category",
        "sets", "reps", "weight", "created_at", "updated_at"
    }
    assert expected_columns.issubset(columns)
    
    # Check foreign keys
    foreign_keys = inspector.get_foreign_keys("exercise")
    assert any(fk["referred_table"] == "workout" for fk in foreign_keys)


def test_workout_model_can_be_instantiated():
    """Test that the Workout model can be instantiated."""
    workout = Workout(
        name="Test Workout",
        description="Test description",
        duration_minutes=60,
        is_completed=False
    )
    assert workout.name == "Test Workout"
    assert workout.description == "Test description"
    assert workout.duration_minutes == 60
    assert workout.is_completed is False


def test_exercise_model_can_be_instantiated():
    """Test that the Exercise model can be instantiated."""
    exercise = Exercise(
        name="Test Exercise",
        category="Strength",
        sets=3,
        reps=10,
        weight=50.0
    )
    assert exercise.name == "Test Exercise"
    assert exercise.category == "Strength"
    assert exercise.sets == 3
    assert exercise.reps == 10
    assert exercise.weight == 50.0