import pytest
from sqlalchemy.orm import Session
from app.models import User, Item
from app.crud import create_user, get_user, update_user, delete_user

def test_create_user_crud(db: Session):
    """Test user creation through CRUD operations."""
    user_data = {
        "email": "crud@example.com",
        "password": "testpassword",
        "full_name": "CRUD User"
    }
    user = create_user(db, user_data)
    assert user.email == "crud@example.com"
    assert user.full_name == "CRUD User"

def test_get_user_by_email(db: Session):
    """Test retrieving user by email."""
    # First create a user
    user_data = {
        "email": "getuser@example.com",
        "password": "testpassword"
    }
    created_user = create_user(db, user_data)

    # Then retrieve it
    retrieved_user = get_user(db, email="getuser@example.com")
    assert retrieved_user is not None
    assert retrieved_user.email == "getuser@example.com"

def test_update_user_crud(db: Session):
    """Test user update through CRUD operations."""
    user_data = {"email": "update@example.com", "password": "test"}
    user = create_user(db, user_data)

    update_data = {"full_name": "Updated Name"}
    updated_user = update_user(db, user.id, update_data)
    assert updated_user.full_name == "Updated Name"
