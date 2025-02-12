from fastapi.testclient import TestClient
from sqlmodel import Session


from app.core.config import settings
from backend.app.model.user_model import User, UserCreate, UserUpdate
from app.service.user_service import UserService
from app.tests.utils.utils import random_email, random_lower_string


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user(db: Session) -> User:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user_service = UserService(db)
    user = user_service.create_user(user_in)
    return user


def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    user_service = UserService(db)
    user = user_service.get_user_by_email(email=email)
    if not user:
        user_in_create = UserCreate(email=email, password=password)
        user = user_service.create_user(user_in_create)
    else:
        user_in_update = UserUpdate(password=password)
        if not user.id:
            raise Exception("User id not set")
        user_service = UserService(db)
        user = user_service.update_user(user, user_in_update)
    return user_authentication_headers(client=client, email=email, password=password)
