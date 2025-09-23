import pytest
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models import User
from app.utils import generate_password_reset_token, verify_password_reset_token

def test_database_connection(db: Session):
    """Test database connection is working."""
    result = db.execute("SELECT 1")
    assert result.fetchone()[0] == 1

def test_user_model_creation(db: Session):
    """Test creating a user in the database."""
    user_data = {
        "email": "test@example.com",
        "hashed_password": "hashedpassword123",
        "full_name": "Test User"
    }
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"

def test_database_rollback(db: Session):
    """Test database rollback functionality."""
    user = User(email="rollback@example.com", hashed_password="test123")
    db.add(user)
    db.rollback()

    # User should not exist after rollback
    user_check = db.query(User).filter(User.email == "rollback@example.com").first()
    assert user_check is None
