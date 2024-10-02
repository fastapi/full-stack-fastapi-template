import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import crud
from app.core.config import settings
from app.core.security import verify_password
from app.models import User, UserCreate
from app.tests.utils.utils import random_email, random_lower_string


def test_get_users_superuser_me(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test getting the current superuser.

    Args:
        client (TestClient): The test client.
        superuser_token_headers (dict[str, str]): The superuser token headers.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Send a GET request to retrieve the current superuser
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
    current_user = r.json()

    # Assert that the user exists and has the correct attributes
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"]
    assert current_user["email"] == settings.FIRST_SUPERUSER


def test_get_users_normal_user_me(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test getting the current normal user.

    Args:
        client (TestClient): The test client.
        normal_user_token_headers (dict[str, str]): The normal user token headers.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Send a GET request to retrieve the current normal user
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
    current_user = r.json()

    # Assert that the user exists and has the correct attributes
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is False
    assert current_user["email"] == settings.EMAIL_TEST_USER


def test_create_user_new_email(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test creating a new user with a new email.

    Args:
        client (TestClient): The test client.
        superuser_token_headers (dict[str, str]): The superuser token headers.
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Generate random email and password for the new user
    username = random_email()
    password = random_lower_string()
    data = {"email": username, "password": password}
    # Send a POST request to create a new user
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    # Assert that the request was successful
    assert 200 <= r.status_code < 300
    created_user = r.json()
    # Retrieve the user from the database and assert its correctness
    user = crud.get_user_by_email(session=db, email=username)
    assert user
    assert user.email == created_user["email"]
    assert created_user["email"] == username


def test_get_existing_user(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test getting an existing user.

    Args:
        client (TestClient): The test client.
        superuser_token_headers (dict[str, str]): The superuser token headers.
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Create a new user
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    user_id = user.id

    # Send a GET request to retrieve the created user
    r = client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )

    # Assert that the request was successful
    assert 200 <= r.status_code < 300
    api_user = r.json()

    # Retrieve the user from the database and assert its correctness
    existing_user = crud.get_user_by_email(session=db, email=username)
    assert existing_user
    assert existing_user.email == api_user["email"]


def test_get_existing_user_current_user(client: TestClient, db: Session) -> None:
    """
    Test getting the current user as an existing user.

    Args:
        client (TestClient): The test client.
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Create a new user
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    user_id = user.id

    # Log in as the created user
    login_data = {
        "username": username,
        "password": password,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}

    # Send a GET request to retrieve the current user
    r = client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=headers,
    )

    # Assert that the request was successful
    assert 200 <= r.status_code < 300
    api_user = r.json()

    # Retrieve the user from the database and assert its correctness
    existing_user = crud.get_user_by_email(session=db, email=username)
    assert existing_user
    assert existing_user.email == api_user["email"]


def test_get_existing_user_permissions_error(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test getting an existing user with insufficient permissions.

    Args:
        client (TestClient): The test client.
        normal_user_token_headers (dict[str, str]): The normal user token headers.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Attempt to retrieve a user with insufficient privileges
    r = client.get(
        f"{settings.API_V1_STR}/users/{uuid.uuid4()}",
        headers=normal_user_token_headers,
    )

    # Assert that the request was forbidden
    assert r.status_code == 403
    assert r.json() == {"detail": "The user doesn't have enough privileges"}


def test_create_user_existing_username(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test creating a user with an existing username.

    Args:
        client (TestClient): The test client.
        superuser_token_headers (dict[str, str]): The superuser token headers.
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Create a new user
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    crud.create_user(session=db, user_create=user_in)

    # Attempt to create a user with the same email
    data = {"email": username, "password": password}
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = r.json()

    # Assert that the request was unsuccessful
    assert r.status_code == 400
    assert "_id" not in created_user


def test_create_user_by_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test creating a user by a normal user.

    Args:
        client (TestClient): The test client.
        normal_user_token_headers (dict[str, str]): The normal user token headers.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Attempt to create a new user with normal user privileges
    username = random_email()
    password = random_lower_string()
    data = {"email": username, "password": password}
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=normal_user_token_headers,
        json=data,
    )

    # Assert that the request was forbidden
    assert r.status_code == 403


def test_retrieve_users(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test retrieving all users.

    Args:
        client (TestClient): The test client.
        superuser_token_headers (dict[str, str]): The superuser token headers.
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Create two new users
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    crud.create_user(session=db, user_create=user_in)

    username2 = random_email()
    password2 = random_lower_string()
    user_in2 = UserCreate(email=username2, password=password2)
    crud.create_user(session=db, user_create=user_in2)

    # Retrieve all users
    r = client.get(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers)
    all_users = r.json()

    # Assert that multiple users were retrieved
    assert len(all_users["data"]) > 1
    assert "count" in all_users
    for item in all_users["data"]:
        assert "email" in item


def test_read_users_pagination(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test reading users with pagination.

    Args:
        client (TestClient): The test client.
        superuser_token_headers (dict[str, str]): The superuser token headers.
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Create multiple users
    for _ in range(5):
        crud.create_user(
            session=db,
            user_create=UserCreate(
                email=random_email(), password=random_lower_string()
            ),
        )

    # Retrieve users with pagination
    r = client.get(
        f"{settings.API_V1_STR}/users/?skip=1&limit=2", headers=superuser_token_headers
    )
    all_users = r.json()

    # Assert that the pagination works correctly
    assert r.status_code == 200
    assert len(all_users["data"]) == 2
    assert all_users["count"] > 2


def test_update_user_me(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test updating the current user.

    Args:
        client (TestClient): The test client.
        normal_user_token_headers (dict[str, str]): The normal user token headers.
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Update the current user's full name and email
    full_name = "Updated Name"
    email = random_email()
    data = {"full_name": full_name, "email": email}
    r = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        json=data,
    )

    # Assert that the update was successful
    assert r.status_code == 200
    updated_user = r.json()
    assert updated_user["email"] == email
    assert updated_user["full_name"] == full_name

    # Verify the update in the database
    user_query = select(User).where(User.email == email)
    user_db = db.exec(user_query).first()
    assert user_db
    assert user_db.email == email
    assert user_db.full_name == full_name


def test_update_password_me(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test updating the current user's password.

    Args:
        client (TestClient): The test client.
        superuser_token_headers (dict[str, str]): The superuser token headers.
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Update the current user's password
    new_password = random_lower_string()
    data = {
        "current_password": settings.FIRST_SUPERUSER_PASSWORD,
        "new_password": new_password,
    }
    r = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=superuser_token_headers,
        json=data,
    )

    # Assert that the update was successful
    assert r.status_code == 200
    updated_user = r.json()
    assert updated_user["message"] == "Password updated successfully"

    # Verify the password update in the database
    user_query = select(User).where(User.email == settings.FIRST_SUPERUSER)
    user_db = db.exec(user_query).first()
    assert user_db
    assert user_db.email == settings.FIRST_SUPERUSER
    assert verify_password(new_password, user_db.hashed_password)

    # Revert to the old password to keep consistency in test
    old_data = {
        "current_password": new_password,
        "new_password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=superuser_token_headers,
        json=old_data,
    )
    db.refresh(user_db)

    assert r.status_code == 200
    assert verify_password(settings.FIRST_SUPERUSER_PASSWORD, user_db.hashed_password)


def test_update_password_me_incorrect_password(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test updating the current user's password with an incorrect current password.

    Args:
        client (TestClient): The test client.
        superuser_token_headers (dict[str, str]): The superuser token headers.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Attempt to update password with incorrect current password
    new_password = random_lower_string()
    data = {"current_password": new_password, "new_password": new_password}
    r = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=superuser_token_headers,
        json=data,
    )

    # Assert that the update was unsuccessful
    assert r.status_code == 400
    updated_user = r.json()
    assert updated_user["detail"] == "Incorrect password"


def test_update_user_me_email_exists(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test updating the current user's email to an existing email.

    Args:
        client (TestClient): The test client.
        normal_user_token_headers (dict[str, str]): The normal user token headers.
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Create a new user
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)

    # Attempt to update current user's email to an existing email
    data = {"email": user.email}
    r = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        json=data,
    )

    # Assert that the update was unsuccessful
    assert r.status_code == 409
    assert r.json()["detail"] == "User with this email already exists"


def test_update_password_me_same_password_error(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test updating the current user's password to the same password.

    Args:
        client (TestClient): The test client.
        superuser_token_headers (dict[str, str]): The superuser token headers.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Attempt to update password to the same password
    data = {
        "current_password": settings.FIRST_SUPERUSER_PASSWORD,
        "new_password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=superuser_token_headers,
        json=data,
    )

    # Assert that the update was unsuccessful
    assert r.status_code == 400
    updated_user = r.json()
    assert (
        updated_user["detail"] == "New password cannot be the same as the current one"
    )


def test_register_user(client: TestClient, db: Session) -> None:
    """
    Test registering a new user.

    Args:
        client (TestClient): The test client.
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Register a new user
    username = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    data = {"email": username, "password": password, "full_name": full_name}
    r = client.post(
        f"{settings.API_V1_STR}/users/signup",
        json=data,
    )

    # Assert that the registration was successful
    assert r.status_code == 200
    created_user = r.json()
    assert created_user["email"] == username
    assert created_user["full_name"] == full_name

    # Verify the user in the database
    user_query = select(User).where(User.email == username)
    user_db = db.exec(user_query).first()
    assert user_db
    assert user_db.email == username
    assert user_db.full_name == full_name
    assert verify_password(password, user_db.hashed_password)


def test_register_user_already_exists_error(client: TestClient) -> None:
    """
    Test registering a user with an existing email.

    Args:
        client (TestClient): The test client.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Attempt to register a user with an existing email
    password = random_lower_string()
    full_name = random_lower_string()
    data = {
        "email": settings.FIRST_SUPERUSER,
        "password": password,
        "full_name": full_name,
    }
    r = client.post(
        f"{settings.API_V1_STR}/users/signup",
        json=data,
    )

    # Assert that the registration was unsuccessful
    assert r.status_code == 400
    assert r.json()["detail"] == "The user with this email already exists in the system"


def test_update_user(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test updating a user.

    Args:
        client (TestClient): The test client.
        superuser_token_headers (dict[str, str]): The superuser token headers.
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Create a new user
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)

    # Update the user's full name
    data = {"full_name": "Updated_full_name"}
    r = client.patch(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )

    # Assert that the update was successful
    assert r.status_code == 200
    updated_user = r.json()

    assert updated_user["full_name"] == "Updated_full_name"

    # Verify the update in the database
    user_query = select(User).where(User.email == username)
    user_db = db.exec(user_query).first()
    db.refresh(user_db)
    assert user_db
    assert user_db.full_name == "Updated_full_name"


def test_update_user_non_existent(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test updating a non-existent user.

    Args:
        client (TestClient): The test client.
        superuser_token_headers (dict[str, str]): The superuser token headers.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Attempt to update a non-existent user
    data = {"full_name": "Updated_full_name"}
    r = client.patch(
        f"{settings.API_V1_STR}/users/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )

    # Assert that the update was unsuccessful
    assert r.status_code == 404
    assert r.json()["detail"] == "The user with this id does not exist in the system"


def test_update_user_email_exists(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test updating a user's email to an existing email.

    Args:
        client (TestClient): The test client.
        superuser_token_headers (dict[str, str]): The superuser token headers.
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Create two users
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)

    username2 = random_email()
    password2 = random_lower_string()
    user_in2 = UserCreate(email=username2, password=password2)
    user2 = crud.create_user(session=db, user_create=user_in2)

    # Attempt to update the first user's email to the second user's email
    data = {"email": user2.email}
    r = client.patch(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )

    # Assert that the update was unsuccessful
    assert r.status_code == 409
    assert r.json()["detail"] == "User with this email already exists"


def test_delete_user_me(client: TestClient, db: Session) -> None:
    """
    Test deleting the current user.

    Args:
        client (TestClient): The test client.
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Create a new user
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    user_id = user.id

    # Log in as the created user
    login_data = {
        "username": username,
        "password": password,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}

    # Delete the current user
    r = client.delete(
        f"{settings.API_V1_STR}/users/me",
        headers=headers,
    )

    # Assert that the deletion was successful
    assert r.status_code == 200
    deleted_user = r.json()
    assert deleted_user["message"] == "User deleted successfully"

    # Verify that the user no longer exists in the database
    result = db.exec(select(User).where(User.id == user_id)).first()
    assert result is None

    user_query = select(User).where(User.id == user_id)
    user_db = db.execute(user_query).first()
    assert user_db is None


def test_delete_user_me_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test deleting the current user as a superuser.

    Args:
        client (TestClient): The test client.
        superuser_token_headers (dict[str, str]): The superuser token headers.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Attempt to delete the superuser account
    r = client.delete(
        f"{settings.API_V1_STR}/users/me",
        headers=superuser_token_headers,
    )

    # Assert that the deletion was unsuccessful
    assert r.status_code == 403
    response = r.json()
    assert response["detail"] == "Super users are not allowed to delete themselves"


def test_delete_user_super_user(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test deleting a user as a superuser.

    Args:
        client (TestClient): The test client.
        superuser_token_headers (dict[str, str]): The superuser token headers.
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Create a new user
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    user_id = user.id

    # Delete the user as a superuser
    r = client.delete(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )

    # Assert that the deletion was successful
    assert r.status_code == 200
    deleted_user = r.json()
    assert deleted_user["message"] == "User deleted successfully"

    # Verify that the user no longer exists in the database
    result = db.exec(select(User).where(User.id == user_id)).first()
    assert result is None


def test_delete_user_self(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test deleting the current user as a superuser.

    Args:
        client (TestClient): The test client.
        superuser_token_headers (dict[str, str]): The superuser token headers.
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
    """
    # Attempt to delete the superuser account
    super_user = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert super_user
    r = client.delete(
        f"{settings.API_V1_STR}/users/{super_user.id}",
        headers=superuser_token_headers,
    )

    # Assert that the deletion was unsuccessful
    assert r.status_code == 403
    assert r.json()["detail"] == "Super users are not allowed to delete themselves"


def test_delete_user_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test that the delete_user_not_found function raises an HTTPException when the user does not exist.
    """
    # Attempt to delete a non-existent user
    r = client.delete(
        f"{settings.API_V1_STR}/users/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )

    # Assert that the deletion was unsuccessful
    assert r.status_code == 404
    assert r.json()["detail"] == "User not found"


def test_delete_user_current_super_user_error(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test that the delete_user_current_super_user_error function raises an HTTPException when the current superuser tries to delete another superuser.
    """
    # Attempt to delete the superuser account
    super_user = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert super_user
    user_id = super_user.id

    r = client.delete(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )

    # Assert that the deletion was unsuccessful
    assert r.status_code == 403
    assert r.json()["detail"] == "Super users are not allowed to delete themselves"


def test_delete_user_without_privileges(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test that the delete_user_without_privileges function raises an HTTPException when the user does not have enough privileges.
    """
    # Create a new user
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)

    # Attempt to delete the user as a normal user
    r = client.delete(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=normal_user_token_headers,
    )

    # Assert that the deletion was unsuccessful
    assert r.status_code == 403
    assert r.json()["detail"] == "The user doesn't have enough privileges"
