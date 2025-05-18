"""
Tests for user service.

This module tests the user service functionality.
"""
import uuid
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session

from app.core.security import verify_password
from app.modules.users.domain.models import User
from app.modules.users.domain.models import UserCreate, UserUpdate
from app.modules.users.services.user_service import UserService
from app.shared.exceptions import NotFoundException, ValidationException
from app.tests.utils.utils import random_email, random_lower_string

import pytest


def test_create_user(user_service: UserService) -> None:
    """Test creating a user."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = user_service.create_user(user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")


def test_create_user_duplicate_email(user_service: UserService) -> None:
    """Test creating a user with duplicate email fails."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user_service.create_user(user_in)

    # Try to create another user with the same email
    with pytest.raises(ValidationException):
        user_service.create_user(user_in)


def test_authenticate_user(user_service: UserService) -> None:
    """Test authenticating a user."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = user_service.create_user(user_in)

    # Use the auth service for authentication
    authenticated_user = user_service.get_user_by_email(email)
    assert authenticated_user is not None
    assert verify_password(password, authenticated_user.hashed_password)
    assert user.email == authenticated_user.email


def test_get_non_existent_user(user_service: UserService) -> None:
    """Test getting a non-existent user raises exception."""
    non_existent_id = uuid.uuid4()

    with pytest.raises(NotFoundException):
        user_service.get_user(non_existent_id)


def test_check_if_user_is_active(user_service: UserService) -> None:
    """Test checking if user is active."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = user_service.create_user(user_in)
    assert user.is_active is True


def test_check_if_user_is_superuser(user_service: UserService) -> None:
    """Test checking if user is superuser."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = user_service.create_user(user_in)
    assert user.is_superuser is True


def test_check_if_user_is_superuser_normal_user(user_service: UserService) -> None:
    """Test checking if normal user is not superuser."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = user_service.create_user(user_in)
    assert user.is_superuser is False


def test_get_user(db: Session, user_service: UserService) -> None:
    """Test getting a user by ID."""
    password = random_lower_string()
    email = random_email()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = user_service.create_user(user_in)
    user_2 = user_service.get_user(user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_update_user(db: Session, user_service: UserService) -> None:
    """Test updating a user."""
    password = random_lower_string()
    email = random_email()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = user_service.create_user(user_in)
    new_password = random_lower_string()
    user_in_update = UserUpdate(password=new_password, is_superuser=True)
    updated_user = user_service.update_user(user.id, user_in_update)
    assert updated_user
    assert user.email == updated_user.email
    assert verify_password(new_password, updated_user.hashed_password)


def test_update_user_me(db: Session, user_service: UserService) -> None:
    """Test user updating their own profile."""
    password = random_lower_string()
    email = random_email()
    user_in = UserCreate(email=email, password=password)
    user = user_service.create_user(user_in)

    # Update full name
    new_name = "New Name"
    from app.modules.users.domain.models import UserUpdateMe
    update_data = UserUpdateMe(full_name=new_name)
    updated_user = user_service.update_user_me(user, update_data)

    assert updated_user.full_name == new_name
    assert updated_user.email == email