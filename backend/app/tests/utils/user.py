from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import User, UserCreate, UserUpdate
from app.repositories.users import UserRepository
from app.services.users import UserService
from app.tests.utils.utils import random_email, random_lower_string


def user_service(session: Session) -> UserService:
    return UserService(repository=UserRepository(session=session))


def create_random_user(session: Session) -> User:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = user_service(session).create(user_create=user_in)
    return user


def get_user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def get_superuser_token_headers(client: TestClient) -> dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


def get_authentication_token_from_email(
    *, client: TestClient, email: str, session: Session
) -> dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    user = user_service(session).repository.get_by_email(email=email)
    if not user:
        user_in_create = UserCreate(email=email, password=password)
        user = user_service(session).create(user_create=user_in_create)
    else:
        user_in_update = UserUpdate(password=password)
        if not user.id:
            raise Exception("User id not set")
        user = user_service(session).update(db_user=user, user_update=user_in_update)

    return get_user_authentication_headers(
        client=client, email=email, password=password
    )
