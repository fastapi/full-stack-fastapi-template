from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.core.db import engine, init_db
from app.models import UserCreate


def test_engine() -> None:
    """
    Test database engine initialization.

    This function tests if the database engine is properly initialized.
    The function is not protected and does not require authentication.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the test fails.

    Notes:
        This test checks if the engine object is not None.
    """
    # Test if the database engine is properly initialized
    assert engine is not None


def test_init_db_creates_superuser(db: Session) -> None:
    """
    Test superuser creation during database initialization.

    This function tests if init_db creates a superuser when one doesn't exist.
    The function is not protected and does not require authentication.

    Args:
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.

    Notes:
        This test ensures that a superuser is created with the correct attributes
        when init_db is called and no superuser exists.
    """

    # Ensure the superuser doesn't exist by deleting it if present
    user = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    if user:
        crud.delete_user(session=db, user_id=user.id)

    # Run init_db to create the superuser
    init_db(db)

    # Check if the superuser was created with correct attributes
    user = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert user is not None
    assert user.email == settings.FIRST_SUPERUSER
    assert user.is_superuser


def test_init_db_doesnt_create_duplicate_superuser(db: Session) -> None:
    """
    Test prevention of duplicate superuser creation.

    This function tests if init_db doesn't create a duplicate superuser when one already exists.
    The function is not protected and does not require authentication.

    Args:
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.

    Notes:
        This test ensures that only one superuser exists after running init_db
        when a superuser is already present in the database.
    """

    # Ensure the superuser exists by creating one if not present
    existing_user = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    if not existing_user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        existing_user = crud.create_user(session=db, user_create=user_in)

    # Run init_db
    init_db(db)

    # Check that only one superuser exists and it's the same as the existing one
    users = crud.get_users(session=db)
    superusers = [user for user in users if user.email == settings.FIRST_SUPERUSER]
    assert len(superusers) == 1
    assert superusers[0].id == existing_user.id


def test_init_db_with_migrations(db: Session) -> None:
    """
    Test database initialization with migrations.

    This function tests if init_db creates a superuser when run with migrations.
    The function is not protected and does not require authentication.

    Args:
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.

    Notes:
        This test verifies that a superuser is created with the correct attributes
        when init_db is run, simulating a scenario with migrations.
    """

    # Run init_db
    init_db(db)

    # Verify that the superuser is created with correct attributes
    user = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert user is not None
    assert user.email == settings.FIRST_SUPERUSER
    assert user.is_superuser
