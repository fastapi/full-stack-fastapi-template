import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import crud
from app.constants import (
    BAD_REQUEST_CODE,
    CONFLICT_CODE,
    FORBIDDEN_CODE,
    NOT_FOUND_CODE,
    OK_CODE,
)
from app.core.config import settings
from app.core.security import verify_password
from app.models import User, UserCreate
from app.tests.utils.test_helpers import random_email, random_lower_string


# Helper functions to reduce complexity
def create_test_user_data():
    """Create random user data for testing."""
    return {
        "username": random_email(),
        "password": random_lower_string(),
    }


def create_user_in_db(db: Session, username: str = None, password: str = None):
    """Create a user in the database and return it."""
    if username is None:
        username = random_email()
    if password is None:
        password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    return crud.create_user(session=db, user_create=user_in)


def authenticate_user(client: TestClient, username: str, password: str):
    """Authenticate a user and return headers."""
    login_data = {"username": username, USER_PASSWORD_KEY: password}
    response = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    response_data = response.json()
    access_token = response_data["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

# Constants for commonly used strings
USER_EMAIL_KEY = "email"
USER_PASSWORD_KEY = "password"
USER_FULL_NAME_KEY = "full_name"
USER_CURRENT_PASSWORD_KEY = "current_password"
USER_NEW_PASSWORD_KEY = "new_password"
USERS_ME_ENDPOINT = "/users/me"
USERS_ENDPOINT = "/users/"
USERS_ME_PASSWORD_ENDPOINT = "/users/me/password"
USERS_SIGNUP_ENDPOINT = "/users/signup"
USERS_BASE_ENDPOINT = "/users/"  # For constructing /users/{id} endpoints
ERROR_DETAIL_KEY = "detail"
UPDATED_FULL_NAME = "Updated_full_name"


def test_get_users_superuser_me(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    response = client.get(f"{settings.API_V1_STR}{USERS_ME_ENDPOINT}", headers=superuser_token_headers)
    current_user = response.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"]
    assert current_user[USER_EMAIL_KEY] == settings.FIRST_SUPERUSER


def test_get_users_normal_user_me(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    response = client.get(f"{settings.API_V1_STR}{USERS_ME_ENDPOINT}", headers=normal_user_token_headers)
    current_user = response.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is False
    assert current_user[USER_EMAIL_KEY] == settings.EMAIL_TEST_USER


def test_create_user_new_email(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    with (
        patch("app.utils.send_email", return_value=None),
        patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
        patch("app.core.config.settings.SMTP_USER", "admin@example.com"),
    ):
        test_data = create_test_user_data()
        user_data = {USER_EMAIL_KEY: test_data["username"], USER_PASSWORD_KEY: test_data["password"]}
        response = client.post(
            f"{settings.API_V1_STR}{USERS_ENDPOINT}",
            headers=superuser_token_headers,
            json=user_data,
        )
        assert response.status_code == OK_CODE
        created_user = response.json()
        user = crud.get_user_by_email(session=db, email=test_data["username"])
        assert user
        assert user.email == created_user[USER_EMAIL_KEY]


def test_get_existing_user(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    user = create_user_in_db(db)
    response = client.get(
        f"{settings.API_V1_STR}{USERS_BASE_ENDPOINT}{user.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == OK_CODE
    api_user = response.json()
    existing_user = crud.get_user_by_email(session=db, email=user.email)
    assert existing_user
    assert existing_user.email == api_user[USER_EMAIL_KEY]


def test_get_existing_user_current_user(client: TestClient, db: Session) -> None:
    test_data = create_test_user_data()
    user = create_user_in_db(db, test_data["username"], test_data["password"])
    headers = authenticate_user(client, test_data["username"], test_data["password"])

    response = client.get(
        f"{settings.API_V1_STR}{USERS_BASE_ENDPOINT}{user.id}",
        headers=headers,
    )
    assert response.status_code == OK_CODE
    api_user = response.json()
    existing_user = crud.get_user_by_email(session=db, email=test_data["username"])
    assert existing_user
    assert existing_user.email == api_user[USER_EMAIL_KEY]


def test_get_existing_user_permissions_error(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}{USERS_BASE_ENDPOINT}{uuid.uuid4()}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == FORBIDDEN_CODE
    assert response.json() == {ERROR_DETAIL_KEY: "The user doesn't have enough privileges"}


def test_create_user_existing_username(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    test_data = create_test_user_data()
    create_user_in_db(db, test_data["username"], test_data["password"])
    user_data = {USER_EMAIL_KEY: test_data["username"], USER_PASSWORD_KEY: test_data["password"]}
    response = client.post(
        f"{settings.API_V1_STR}{USERS_ENDPOINT}",
        headers=superuser_token_headers,
        json=user_data,
    )
    created_user = response.json()
    assert response.status_code == BAD_REQUEST_CODE
    assert "_id" not in created_user


def test_create_user_by_normal_user(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    username = random_email()
    password = random_lower_string()
    user_data = {USER_EMAIL_KEY: username, USER_PASSWORD_KEY: password}
    response = client.post(
        f"{settings.API_V1_STR}{USERS_ENDPOINT}",
        headers=normal_user_token_headers,
        json=user_data,
    )
    assert response.status_code == FORBIDDEN_CODE


def test_retrieve_users(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    create_user_in_db(db)
    create_user_in_db(db)

    response = client.get(f"{settings.API_V1_STR}{USERS_ENDPOINT}", headers=superuser_token_headers)
    all_users = response.json()

    assert len(all_users["data"]) > 1
    assert "count" in all_users
    for user_data in all_users["data"]:
        assert USER_EMAIL_KEY in user_data


def test_update_user_me(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    full_name = "Updated Name"
    email = random_email()
    update_data = {USER_FULL_NAME_KEY: full_name, USER_EMAIL_KEY: email}
    response = client.patch(
        f"{settings.API_V1_STR}{USERS_ME_ENDPOINT}",
        headers=normal_user_token_headers,
        json=update_data,
    )
    assert response.status_code == OK_CODE
    updated_user = response.json()
    assert updated_user[USER_EMAIL_KEY] == email
    assert updated_user[USER_FULL_NAME_KEY] == full_name

    user_query = select(User).where(User.email == email)
    user_db = db.exec(user_query).first()
    assert user_db
    assert user_db.email == email
    assert user_db.full_name == full_name


def test_update_password_me(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    new_password = random_lower_string()
    password_data = {
        USER_CURRENT_PASSWORD_KEY: settings.FIRST_SUPERUSER_PASSWORD,
        USER_NEW_PASSWORD_KEY: new_password,
    }
    response = client.patch(
        f"{settings.API_V1_STR}{USERS_ME_PASSWORD_ENDPOINT}",
        headers=superuser_token_headers,
        json=password_data,
    )
    assert response.status_code == OK_CODE
    updated_user = response.json()
    assert updated_user["message"] == "Password updated successfully"

    user_query = select(User).where(User.email == settings.FIRST_SUPERUSER)
    user_db = db.exec(user_query).first()
    assert user_db
    assert verify_password(new_password, user_db.hashed_password)

    # Revert to the old password to keep consistency in test
    _revert_superuser_password(client, superuser_token_headers, new_password)


def _revert_superuser_password(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    new_password: str,
) -> None:
    """Helper to revert superuser password for test consistency."""
    revert_data = {
        USER_CURRENT_PASSWORD_KEY: new_password,
        USER_NEW_PASSWORD_KEY: settings.FIRST_SUPERUSER_PASSWORD,
    }
    response = client.patch(
        f"{settings.API_V1_STR}{USERS_ME_PASSWORD_ENDPOINT}",
        headers=superuser_token_headers,
        json=revert_data,
    )
    assert response.status_code == OK_CODE


def test_update_password_me_incorrect_password(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    new_password = random_lower_string()
    password_data = {"current_password": new_password, "new_password": new_password}
    response = client.patch(
        f"{settings.API_V1_STR}{USERS_ME_PASSWORD_ENDPOINT}",
        headers=superuser_token_headers,
        json=password_data,
    )
    assert response.status_code == BAD_REQUEST_CODE
    updated_user = response.json()
    assert updated_user[ERROR_DETAIL_KEY] == "Incorrect password"


def test_update_user_me_email_exists(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    user = create_user_in_db(db)

    update_data = {USER_EMAIL_KEY: user.email}
    response = client.patch(
        f"{settings.API_V1_STR}{USERS_ME_ENDPOINT}",
        headers=normal_user_token_headers,
        json=update_data,
    )
    assert response.status_code == CONFLICT_CODE
    assert response.json()[ERROR_DETAIL_KEY] == "User with this email already exists"


def test_update_password_me_same_password_error(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    password_data = {
        USER_CURRENT_PASSWORD_KEY: settings.FIRST_SUPERUSER_PASSWORD,
        USER_NEW_PASSWORD_KEY: settings.FIRST_SUPERUSER_PASSWORD,
    }
    response = client.patch(
        f"{settings.API_V1_STR}{USERS_ME_PASSWORD_ENDPOINT}",
        headers=superuser_token_headers,
        json=password_data,
    )
    assert response.status_code == BAD_REQUEST_CODE
    updated_user = response.json()
    assert (
        updated_user[ERROR_DETAIL_KEY] == "New password cannot be the same as the current one"
    )


def test_register_user(client: TestClient, db: Session) -> None:
    test_data = create_test_user_data()
    full_name = random_lower_string()
    signup_data = {
        USER_EMAIL_KEY: test_data["username"],
        USER_PASSWORD_KEY: test_data["password"],
        USER_FULL_NAME_KEY: full_name
    }
    response = client.post(
        f"{settings.API_V1_STR}{USERS_SIGNUP_ENDPOINT}",
        json=signup_data,
    )
    assert response.status_code == OK_CODE
    created_user = response.json()
    assert created_user[USER_EMAIL_KEY] == test_data["username"]
    assert created_user[USER_FULL_NAME_KEY] == full_name

    user_query = select(User).where(User.email == test_data["username"])
    user_db = db.exec(user_query).first()
    assert user_db
    assert user_db.email == test_data["username"]
    assert user_db.full_name == full_name
    assert verify_password(test_data["password"], user_db.hashed_password)


def test_register_user_already_exists_error(client: TestClient) -> None:
    password = random_lower_string()
    full_name = random_lower_string()
    signup_data = {
        USER_EMAIL_KEY: settings.FIRST_SUPERUSER,
        USER_PASSWORD_KEY: password,
        USER_FULL_NAME_KEY: full_name,
    }
    response = client.post(
        f"{settings.API_V1_STR}{USERS_SIGNUP_ENDPOINT}",
        json=signup_data,
    )
    assert response.status_code == BAD_REQUEST_CODE
    assert response.json()[ERROR_DETAIL_KEY] == "The user with this email already exists in the system"


def test_update_user(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    user = create_user_in_db(db)

    update_data = {USER_FULL_NAME_KEY: UPDATED_FULL_NAME}
    response = client.patch(
        f"{settings.API_V1_STR}{USERS_BASE_ENDPOINT}{user.id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == OK_CODE
    updated_user = response.json()

    assert updated_user[USER_FULL_NAME_KEY] == UPDATED_FULL_NAME

    user_query = select(User).where(User.email == user.email)
    user_db = db.exec(user_query).first()
    db.refresh(user_db)
    assert user_db
    assert user_db.full_name == UPDATED_FULL_NAME


def test_update_user_not_exists(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    update_data = {USER_FULL_NAME_KEY: UPDATED_FULL_NAME}
    response = client.patch(
        f"{settings.API_V1_STR}{USERS_BASE_ENDPOINT}{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == NOT_FOUND_CODE
    assert response.json()[ERROR_DETAIL_KEY] == "The user with this id does not exist in the system"


def test_update_user_email_exists(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    user = create_user_in_db(db)
    second_user = create_user_in_db(db)

    update_data = {USER_EMAIL_KEY: second_user.email}
    response = client.patch(
        f"{settings.API_V1_STR}{USERS_BASE_ENDPOINT}{user.id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == CONFLICT_CODE
    assert response.json()[ERROR_DETAIL_KEY] == "User with this email already exists"


def test_delete_user_me(client: TestClient, db: Session) -> None:
    test_data = create_test_user_data()
    user = create_user_in_db(db, test_data["username"], test_data["password"])
    headers = authenticate_user(client, test_data["username"], test_data["password"])

    response = client.delete(
        f"{settings.API_V1_STR}{USERS_ME_ENDPOINT}",
        headers=headers,
    )
    assert response.status_code == OK_CODE
    deleted_user = response.json()
    assert deleted_user["message"] == "User deleted successfully"
    
    # Verify user is deleted
    deleted_user_check = db.exec(select(User).where(User.id == user.id)).first()
    assert deleted_user_check is None


def test_delete_user_me_as_superuser(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}{USERS_ME_ENDPOINT}",
        headers=superuser_token_headers,
    )
    assert response.status_code == FORBIDDEN_CODE
    response_content = response.json()
    assert response_content[ERROR_DETAIL_KEY] == "Super users are not allowed to delete themselves"


def test_delete_user_super_user(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    user = create_user_in_db(db)
    response = client.delete(
        f"{settings.API_V1_STR}{USERS_BASE_ENDPOINT}{user.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == OK_CODE
    deleted_user = response.json()
    assert deleted_user["message"] == "User deleted successfully"
    deleted_user_check = db.exec(select(User).where(User.id == user.id)).first()
    assert deleted_user_check is None


def test_delete_user_not_found(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}{USERS_BASE_ENDPOINT}{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == NOT_FOUND_CODE
    assert response.json()[ERROR_DETAIL_KEY] == "User not found"


def test_delete_user_current_super_user_error(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    super_user = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert super_user
    user_id = super_user.id

    response = client.delete(
        f"{settings.API_V1_STR}{USERS_BASE_ENDPOINT}{user_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == FORBIDDEN_CODE
    assert response.json()[ERROR_DETAIL_KEY] == "Super users are not allowed to delete themselves"


def test_delete_user_without_privileges(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    user = create_user_in_db(db)

    response = client.delete(
        f"{settings.API_V1_STR}{USERS_BASE_ENDPOINT}{user.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == FORBIDDEN_CODE
    assert response.json()[ERROR_DETAIL_KEY] == "The user doesn't have enough privileges"
