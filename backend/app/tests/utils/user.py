from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import User, UserCreate
from app.tests.utils.utils import random_email, random_lower_string


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> dict[str, str]:
    """
    Generate authentication headers for a user.

    This function creates and returns a valid token for the user with the given email and password.

    Args:
        client (TestClient): The test client used to make requests.
        email (str): The email of the user.
        password (str): The password of the user.

    Returns:
        dict[str, str]: A dictionary containing the authentication headers.

    Raises:
        None

    Notes:
        The function sends a POST request to obtain an access token and then creates the authentication headers.
    """
    # Prepare the login data
    data = {"username": email, "password": password}

    # Send a POST request to obtain an access token
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()

    # Extract the access token from the response
    auth_token = response["access_token"]

    # Create and return the authentication headers
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user(db: Session) -> User:
    """
    Create a random user in the database.

    This function generates random email and password, creates a new user with these credentials, and returns the user object.

    Args:
        db (Session): The database session.

    Returns:
        User: The created user object.

    Raises:
        None

    Notes:
        This function uses utility functions to generate random email and password.
    """
    # Generate random email and password
    email = random_email()
    password = random_lower_string()

    # Create a new user with the random email and password
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)

    return user


def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> dict[str, str]:
    """
    Get or create a user and return their authentication token.

    This function returns a valid token for the user with the given email. If the user doesn't exist, it is created first.

    Args:
        client (TestClient): The test client used to make requests.
        email (str): The email of the user.
        db (Session): The database session.

    Returns:
        dict[str, str]: A dictionary containing the authentication headers.

    Raises:
        None

    Notes:
        If the user already exists, their password is updated before generating the authentication token.
    """
    # Generate a random password
    password = random_lower_string()

    # Try to get the user by email
    user = crud.get_user_by_email(session=db, email=email)

    if not user:
        # If the user doesn't exist, create a new one
        user_in_create = UserCreate(email=email, password=password)
        user = crud.create_user(session=db, user_create=user_in_create)
    else:
        # If the user exists, update their password
        user = crud.update_user_password(
            session=db, db_user=user, new_password=password
        )

    # Get and return the authentication headers for the user
    return user_authentication_headers(client=client, email=email, password=password)
