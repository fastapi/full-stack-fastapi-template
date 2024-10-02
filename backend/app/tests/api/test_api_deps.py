from unittest.mock import MagicMock, patch

import jwt
import pytest
from fastapi import HTTPException
from sqlmodel import Session, select, text

from app import crud
from app.api import deps
from app.models import TokenPayload, UserCreate
from app.tests.utils.utils import random_email, random_lower_string


def test_get_db() -> None:
    """
    Test database session retrieval.

    This function tests that the get_db function successfully retrieves a database session.
    The function is not protected and should be accessible without authentication.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the test fails.

    Notes:
        This test creates a database session, performs a test operation,
        and ensures the session is properly closed and disposed.
    """
    # Get a database session using the get_db function
    db = next(deps.get_db())
    # Assert that the returned object is an instance of Session
    assert isinstance(db, Session)
    try:
        # Perform a test operation to ensure the session is working
        db.exec(select(text("1")))
        # Rollback any changes to keep the database clean
        db.rollback()
    finally:
        # Ensure the session is closed and connections are returned to the pool
        db.close()

    # Flush the connection pool to release all connections
    deps.engine.dispose()  # type: ignore[attr-defined]


def test_get_current_user_valid_token(db: Session) -> None:
    """
    Test current user retrieval with valid token.

    This function tests that the get_current_user function successfully retrieves the current user
    when provided with a valid token. The function is protected and requires authentication.

    Args:
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.

    Notes:
        This test creates a random user, mocks a valid token, and verifies
        that the correct user is retrieved.
    """
    # Create a random user
    email = random_email()
    password = random_lower_string()
    user = crud.create_user(
        session=db, user_create=UserCreate(email=email, password=password)
    )

    # Create a token payload with the user's ID
    token_payload = TokenPayload(sub=str(user.id))
    token = MagicMock()

    # Mock the jwt.decode function to return our token payload
    with patch("jwt.decode", return_value=token_payload.model_dump()):
        # Call get_current_user and check if it returns the correct user
        current_user = deps.get_current_user(db, token)
        assert current_user.id == user.id
        assert current_user.email == email


def test_get_current_user_invalid_token(db: Session) -> None:
    """
    Test current user retrieval with invalid token.

    This function tests that the get_current_user function raises an HTTPException
    when provided with an invalid token. The function is protected and requires authentication.

    Args:
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.

    Notes:
        This test mocks an invalid token and verifies that the correct exception is raised.
    """
    token = MagicMock()

    # Mock jwt.decode to raise an InvalidTokenError
    with patch("jwt.decode", side_effect=jwt.exceptions.InvalidTokenError):
        # Check if get_current_user raises the correct HTTPException
        with pytest.raises(HTTPException) as exc_info:
            deps.get_current_user(db, token)
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Could not validate credentials"


def test_get_current_user_user_not_found(db: Session) -> None:
    """
    Test current user retrieval with non-existent user.

    This function tests that the get_current_user function raises an HTTPException
    when the user associated with the token is not found in the database.
    The function is protected and requires authentication.

    Args:
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.

    Notes:
        This test mocks a token with a non-existent user ID and verifies
        that the correct exception is raised.
    """
    # Create a token payload with a non-existent user ID
    token_payload = TokenPayload(sub="00000000-0000-0000-0000-000000000000")
    token = MagicMock()

    # Mock jwt.decode to return our token payload
    with patch("jwt.decode", return_value=token_payload.model_dump()):
        # Check if get_current_user raises the correct HTTPException
        with pytest.raises(HTTPException) as exc_info:
            deps.get_current_user(db, token)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "User not found"


def test_get_current_user_inactive_user(db: Session) -> None:
    """
    Test current user retrieval with inactive user.

    This function tests that the get_current_user function raises an HTTPException
    when the user associated with the token is inactive.
    The function is protected and requires authentication.

    Args:
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.

    Notes:
        This test creates an inactive user, mocks a token for that user,
        and verifies that the correct exception is raised.
    """
    # Create an inactive user
    email = random_email()
    password = random_lower_string()
    user = crud.create_user(
        session=db,
        user_create=UserCreate(email=email, password=password, is_active=False),
    )

    # Create a token payload with the inactive user's ID
    token_payload = TokenPayload(sub=str(user.id))
    token = MagicMock()

    # Mock jwt.decode to return our token payload
    with patch("jwt.decode", return_value=token_payload.model_dump()):
        # Check if get_current_user raises the correct HTTPException
        with pytest.raises(HTTPException) as exc_info:
            deps.get_current_user(db, token)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Inactive user"


def test_get_current_active_superuser(db: Session) -> None:
    """
    Test current active superuser retrieval.

    This function tests that the get_current_active_superuser function
    successfully retrieves the current superuser.
    The function is protected and requires superuser authentication.

    Args:
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.

    Notes:
        This test creates a superuser and verifies that the function
        correctly identifies and returns the superuser.
    """
    # Create a superuser
    email = random_email()
    password = random_lower_string()
    superuser = crud.create_user(
        session=db,
        user_create=UserCreate(email=email, password=password, is_superuser=True),
    )

    # Call get_current_active_superuser and check if it returns the correct superuser
    current_user = deps.get_current_active_superuser(superuser)
    assert current_user.id == superuser.id
    assert current_user.is_superuser


def test_get_current_active_superuser_not_superuser(db: Session) -> None:
    """
    Test current active superuser retrieval with non-superuser.

    This function tests that the get_current_active_superuser function
    raises an HTTPException when the user is not a superuser.
    The function is protected and requires superuser authentication.

    Args:
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.

    Notes:
        This test creates a regular user (not a superuser) and verifies
        that the correct exception is raised when trying to access
        superuser-only functionality.
    """
    # Create a regular user (not a superuser)
    email = random_email()
    password = random_lower_string()
    user = crud.create_user(
        session=db,
        user_create=UserCreate(email=email, password=password, is_superuser=False),
    )

    # Check if get_current_active_superuser raises the correct HTTPException
    with pytest.raises(HTTPException) as exc_info:
        deps.get_current_active_superuser(user)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "The user doesn't have enough privileges"
