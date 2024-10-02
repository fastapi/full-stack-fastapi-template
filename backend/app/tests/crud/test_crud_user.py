from fastapi.encoders import jsonable_encoder
from sqlmodel import Session

from app import crud
from app.core.security import verify_password
from app.models import User, UserCreate, UserUpdate
from app.tests.utils.utils import random_email, random_lower_string


def test_create_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")


def test_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    authenticated_user = crud.authenticate(session=db, email=email, password=password)
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user = crud.authenticate(session=db, email=email, password=password)
    assert user is None


def test_check_if_user_is_active(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.is_active is True


def test_check_if_user_is_active_inactive(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, disabled=True)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.is_active


def test_check_if_user_is_superuser(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.is_superuser is True


def test_check_if_user_is_superuser_normal_user(db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.is_superuser is False


def test_get_user(db: Session) -> None:
    password = random_lower_string()
    username = random_email()
    user_in = UserCreate(email=username, password=password, is_superuser=True)
    user = crud.create_user(session=db, user_create=user_in)
    user_2 = db.get(User, user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_update_user_attributes(db: Session) -> None:
    """
    Test updating user attributes.

    This test verifies that the update_user_attributes function correctly updates
    a user's attributes in the database.

    Args:
        db: The database session.

    Returns:
        None

    Raises:
        AssertionError: If the user attributes are not updated correctly.
    """
    # Create a new user
    password = random_lower_string()
    email = random_email()
    user_in = UserCreate(email=email, password=password, is_superuser=False)
    user = crud.create_user(session=db, user_create=user_in)

    # Update user attributes
    new_email = random_email()
    user_in_update = UserUpdate(email=new_email, is_superuser=True)
    updated_user = crud.update_user_attributes(
        session=db, db_user=user, user_in=user_in_update
    )

    # Verify the updates
    assert updated_user.email == new_email
    assert updated_user.is_superuser is True
    assert updated_user.id == user.id  # Ensure it's the same user

    # Fetch the user from the database to double-check
    db.refresh(user)
    assert user.email == new_email
    assert user.is_superuser is True


def test_update_user_password(db: Session) -> None:
    """
    Test updating user password.

    This test verifies that the update_user_password function correctly updates
    a user's password in the database.

    Args:
        db: The database session.

    Returns:
        None

    Raises:
        AssertionError: If the user password is not updated correctly.
    """
    # Create a new user
    password = random_lower_string()
    email = random_email()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)

    # Update user password
    new_password = random_lower_string()
    updated_user = crud.update_user_password(
        session=db, db_user=user, new_password=new_password
    )

    # Verify the password update
    assert verify_password(new_password, updated_user.hashed_password)
    assert not verify_password(password, updated_user.hashed_password)

    # Fetch the user from the database to double-check
    db.refresh(user)
    assert verify_password(new_password, user.hashed_password)
    assert not verify_password(password, user.hashed_password)
