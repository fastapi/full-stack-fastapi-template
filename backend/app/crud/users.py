import uuid

from sqlmodel import Session, func, select

from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate, UserUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """
    Create a new user.

    Creates a new User object from UserCreate, hashes the password, and adds the user to the database.

    Args:
        session: The database session.
        user_create: The UserCreate object containing user information.

    Returns:
        The newly created User object.

    Raises:
        SQLAlchemyError: If there's an error during database operations.

    Notes:
        This function is not protected and can be called by any authenticated user.
    """
    # Create a new User object from UserCreate, hashing the password
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    # Add the new user to the session, commit changes, and refresh the object
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_user(*, session: Session, user_id: uuid.UUID) -> User | None:
    """
    Get a user by ID.

    Retrieves a user from the database by their UUID.

    Args:
        session: The database session.
        user_id: The UUID of the user to retrieve.

    Returns:
        The User object if found, None otherwise.

    Notes:
        This function is not protected and can be called by any authenticated user.
    """
    # Retrieve a user from the database by their UUID
    return session.get(User, user_id)


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """
    Get a user by email.

    Retrieves a user from the database by their email address.

    Args:
        session: The database session.
        email: The email address of the user to retrieve.

    Returns:
        The User object if found, None otherwise.

    Notes:
        This function is not protected and can be called by any authenticated user.
    """
    # Create a SELECT statement to find a user by email
    statement = select(User).where(User.email == email)
    # Execute the statement and return the first result (or None if not found)
    session_user = session.exec(statement).first()
    return session_user


def get_users(*, session: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """
    Get a list of users.

    Retrieves a list of users from the database with pagination.

    Args:
        session: The database session.
        skip: The number of users to skip (for pagination).
        limit: The maximum number of users to return (for pagination).

    Returns:
        A list of User objects.

    Notes:
        This function is not protected and can be called by any authenticated user.
    """
    # Create a SELECT statement to retrieve users with pagination
    statement = select(User).offset(skip).limit(limit)
    # Execute the statement and return the results as a list
    return list(session.exec(statement).all())


def get_user_count(*, session: Session) -> int:
    """
    Get the total number of users.

    Counts the total number of users in the database.

    Args:
        session: The database session.

    Returns:
        The total number of users as an integer.

    Notes:
        This function is not protected and can be called by any authenticated user.
    """
    # Count the total number of users in the database
    return session.exec(select(func.count()).select_from(User)).one()


def delete_user(*, session: Session, user_id: uuid.UUID) -> User | None:
    """
    Delete a user.

    Deletes a user from the database by their UUID.

    Args:
        session: The database session.
        user_id: The UUID of the user to delete.

    Returns:
        The deleted User object if found and deleted, None otherwise.

    Raises:
        SQLAlchemyError: If there's an error during database operations.

    Notes:
        This function is not protected and can be called by any authenticated user.
    """
    # Retrieve the user by ID
    user = session.get(User, user_id)
    if user:
        # If the user exists, delete them from the database
        session.delete(user)
        session.commit()
    return user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    """
    Authenticate a user.

    Verifies the user's email and password against the database.

    Args:
        session: The database session.
        email: The email address of the user.
        password: The password to verify.

    Returns:
        The authenticated User object if credentials are valid, None otherwise.

    Notes:
        This function is not protected and can be called by any unauthenticated user.
    """
    # Get the user by email
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    # Verify the provided password against the stored hashed password
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def update_user_attributes(
    *, session: Session, db_user: User, user_in: UserUpdate
) -> User:
    """
    Update a user's attributes.

    Updates the attributes of a user in the database.

    Args:
        session: The database session.
        db_user: The User object to update.
        user_in: The UserUpdate object containing the new attribute values.

    Returns:
        The updated User object.

    Raises:
        SQLAlchemyError: If there's an error during database operations.

    Notes:
        This function is not protected and can be called by any authenticated user.
    """
    # Convert the UserUpdate object to a dictionary, excluding unset fields
    user_data = user_in.model_dump(exclude_unset=True)
    # Update the user object with the new data
    db_user.sqlmodel_update(user_data)
    # Save the changes to the database
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_user_password(*, session: Session, db_user: User, new_password: str) -> User:
    """
    Update a user's password.

    Updates the password of a user in the database.

    Args:
        session: The database session.
        db_user: The User object to update.
        new_password: The new password to set.

    Returns:
        The updated User object.

    Raises:
        SQLAlchemyError: If there's an error during database operations.

    Notes:
        This function is not protected and can be called by any authenticated user.
    """
    # Hash the new password
    hashed_password = get_password_hash(new_password)
    # Update the user's hashed password
    db_user.hashed_password = hashed_password
    # Save the changes to the database
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
