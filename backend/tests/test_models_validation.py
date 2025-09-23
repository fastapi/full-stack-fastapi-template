import pytest
from pydantic import ValidationError
from app.models import User, Item

def test_user_model_validation():
    """Test user model field validation."""
    # Valid user data
    valid_data = {
        "email": "test@example.com",
        "hashed_password": "hashedpass123",
        "full_name": "Test User"
    }
    user = User(**valid_data)
    assert user.email == "test@example.com"

def test_user_model_invalid_email():
    """Test user model with invalid email."""
    with pytest.raises(ValidationError):
        User(email="invalid-email", hashed_password="test123")

def test_item_model_creation():
    """Test item model creation and validation."""
    item_data = {
        "title": "Test Item",
        "description": "Test Description",
        "owner_id": 1
    }
    item = Item(**item_data)
    assert item.title == "Test Item"
    assert item.owner_id == 1

def test_model_relationships():
    """Test model relationships and foreign keys."""
    user = User(email="owner@example.com", hashed_password="test123")
    item = Item(title="User's Item", owner_id=1)

    assert item.owner_id == 1
    assert item.title == "User's Item"
