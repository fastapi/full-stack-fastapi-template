from sqlmodel import Session

from app.auth import repository as auth_repository
from app.tests.utils.utils import random_email, random_lower_string
from app.users import repository as users_repository
from app.users.models import UserCreate


def test_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = users_repository.create_user(session=db, user_create=user_in)
    authenticated_user = auth_repository.authenticate(
        session=db, email=email, password=password
    )
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user = auth_repository.authenticate(session=db, email=email, password=password)
    assert user is None
