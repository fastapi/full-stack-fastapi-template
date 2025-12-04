from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError, PendingRollbackError
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import User, UserCreate, UserUpdate
from tests.utils.utils import random_email, random_lower_string


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    if r.status_code != 200:
        raise ValueError(f"Failed to authenticate user {email}: {r.status_code} - {r.text}")
    
    response = r.json()
    auth_token = response.get("access_token")
    if not auth_token:
        raise ValueError(f"Failed to get access token for {email}: {response}")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user(db: Session) -> User:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    return user


def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    Handles session rollback errors that can occur in test environments.
    """
    password = random_lower_string()
    
    # Handle potential session rollback state from previous operations
    try:
        user = crud.get_user_by_email(session=db, email=email)
    except PendingRollbackError:
        db.rollback()
        user = crud.get_user_by_email(session=db, email=email)
    
    if not user:
        user_in_create = UserCreate(email=email, password=password)
        try:
            user = crud.create_user(session=db, user_create=user_in_create)
            db.commit()
        except (IntegrityError, PendingRollbackError):
            # User might have been created by another test concurrently
            # or session is in a bad state - rollback and retry
            db.rollback()
            user = crud.get_user_by_email(session=db, email=email)
            if not user:
                # If still not found after rollback, try creating again
                user = crud.create_user(session=db, user_create=user_in_create)
                db.commit()
            else:
                # User exists now, update password
                user_in_update = UserUpdate(password=password)
                if not user.id:
                    raise Exception("User id not set")
                user = crud.update_user(session=db, db_user=user, user_in=user_in_update)
                db.commit()
    else:
        user_in_update = UserUpdate(password=password)
        if not user.id:
            raise Exception("User id not set")
        try:
            user = crud.update_user(session=db, db_user=user, user_in=user_in_update)
            db.commit()
        except PendingRollbackError:
            db.rollback()
            # Retry getting and updating user after rollback
            user = crud.get_user_by_email(session=db, email=email)
            if user:
                user = crud.update_user(session=db, db_user=user, user_in=user_in_update)
                db.commit()

    return user_authentication_headers(client=client, email=email, password=password)
