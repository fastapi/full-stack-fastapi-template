from unittest.mock import patch

from fastapi.testclient import TestClient
from pytest import mark
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.core.security import verify_password
from app.models import UserCreate
from app.tests.utils.utils import random_email
from app.utils import generate_password_reset_token


def test_get_access_token(client: TestClient) -> None:
    """
    Test the get access token endpoint.

    This function tests the API endpoint for obtaining an access token.

    Args:
        client (TestClient): The test client for making HTTP requests.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    Notes:
        This test prepares login data with superuser credentials, sends a POST request
        to the login endpoint, and verifies the response contains a valid access token.
    """
    # Prepare login data with superuser credentials
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    # Send POST request to login endpoint
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    # Assert successful response and presence of access token
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_login_(client: TestClient) -> None:
    """
    Test the login without rate limit.

    This function tests the login endpoint without rate limiting to ensure
    the limiter is disabled for testing unless explicitly enabled.

    Args:
        client (TestClient): The test client for making HTTP requests.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    Notes:
        This test prepares login data with superuser credentials, sends a POST request
        to the login endpoint, and verifies that the request is not rate limited.
    """
    # Prepare login data with superuser credentials
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    # Send POST request to login endpoint
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    # Assert successful response, indicating no rate limiting
    assert r.status_code == 200, "Request should not be rate limited"


def test_get_access_token_incorrect_password(client: TestClient) -> None:
    """
    Test the get access token endpoint with an incorrect password.

    This function tests the API's response when attempting to obtain
    an access token with an incorrect password.

    Args:
        client (TestClient): The test client for making HTTP requests.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    Notes:
        This test prepares login data with an incorrect password,
        sends a POST request to the login endpoint, and verifies
        that the API returns a bad request response.
    """
    # Prepare login data with incorrect password
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": "incorrect",
    }
    # Send POST request to login endpoint
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    # Assert bad request response
    assert r.status_code == 400


def test_get_access_token_user_not_found(client: TestClient) -> None:
    """
    Test the get access token endpoint with a non-existent user.

    This function tests the API's response when attempting to obtain
    an access token for a user that does not exist in the system.

    Args:
        client (TestClient): The test client for making HTTP requests.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    Notes:
        This test prepares login data with a non-existent user,
        sends a POST request to the login endpoint, and verifies
        that the API returns a bad request response with the correct error message.
    """
    # Prepare login data with non-existent user
    login_data = {
        "username": "nonexistent@example.com",
        "password": "password",
    }
    # Send POST request to login endpoint
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    # Assert bad request response and correct error message
    assert r.status_code == 400
    assert r.json()["detail"] == "Incorrect email or password"


def test_get_access_token_inactive_user(client: TestClient, db: Session) -> None:
    """
    Test the get access token endpoint with an inactive user.

    This function tests the API's response when attempting to obtain
    an access token for an inactive user.

    Args:
        client (TestClient): The test client for making HTTP requests.
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    Notes:
        This test creates an inactive user, prepares login data for this user,
        sends a POST request to the login endpoint, and verifies that the API
        returns a bad request response with the correct error message.
    """
    # Create an inactive user
    user_in = UserCreate(
        email=random_email(),
        password="password1234!",
        is_active=False,
    )
    user = crud.create_user(session=db, user_create=user_in)
    # Prepare login data for inactive user
    login_data = {
        "username": user.email,
        "password": "password1234!",
    }
    # Send POST request to login endpoint
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    # Assert bad request response and correct error message
    assert r.status_code == 400
    assert r.json()["detail"] == "Inactive user"


def test_use_access_token(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test the use access token endpoint.

    This function tests the API endpoint for using an access token.

    Args:
        client (TestClient): The test client for making HTTP requests.
        superuser_token_headers (dict[str, str]): Headers containing the superuser's authentication token.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    Notes:
        This test sends a POST request to the test token endpoint with a superuser token,
        and verifies that the response is successful and contains the expected data.
    """
    # Send POST request to test token endpoint with superuser token
    r = client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers=superuser_token_headers,
    )
    result = r.json()
    # Assert successful response and presence of email in result
    assert r.status_code == 200
    assert "email" in result


@mark.order("last")
def test_recovery_password(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test the recovery password endpoint.

    This function tests the API endpoint for password recovery.

    Args:
        client (TestClient): The test client for making HTTP requests.
        normal_user_token_headers (dict[str, str]): Headers containing a normal user's authentication token.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.
    """

    email = settings.FIRST_SUPERUSER
    # Send POST request to password recovery endpoint
    r = client.post(
        f"{settings.API_V1_STR}/password-recovery/{email}",
        headers=normal_user_token_headers,
    )
    # Assert successful response and correct message
    assert r.status_code == 200
    assert r.json() == {
        "message": "Password recovery email sent if the account exists."
    }


@mark.order("last")
def test_recovery_password_user_not_exits(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test the recovery password endpoint with a non-existent user.

    This function tests the API's response when attempting to recover
    the password for a user that does not exist in the system.

    Args:
        client (TestClient): The test client for making HTTP requests.
        normal_user_token_headers (dict[str, str]): Headers containing a normal user's authentication token.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    Notes:
        This test sends a POST request to the password recovery endpoint with a non-existent email,
        and verifies that the API returns a successful response with the expected message,
        maintaining user privacy by not disclosing whether the account exists.
    """
    # Prepare non-existent email
    email = "this_email_does_not_exist@example.com"
    # Send POST request to password recovery endpoint
    r = client.post(
        f"{settings.API_V1_STR}/password-recovery/{email}",
        headers=normal_user_token_headers,
    )
    # Assert successful response and correct message
    assert r.status_code == 200
    assert r.json() == {
        "message": "Password recovery email sent if the account exists."
    }


@mark.order("last")
def test_reset_password(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test the reset password endpoint.

    This function tests the API endpoint for resetting a user's password.

    Args:
        client (TestClient): The test client for making HTTP requests.
        superuser_token_headers (dict[str, str]): Headers containing the superuser's authentication token.
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    Notes:
        This test generates a password reset token, sends a POST request to reset the password,
        verifies the response, checks the password change in the database, and then reverts
        the password back to the original for other tests to run correctly.
    """
    # Generate password reset token for superuser
    token = generate_password_reset_token(email=settings.FIRST_SUPERUSER)
    # Prepare reset password data
    data = {"new_password": "changethis", "token": token}
    # Send POST request to reset password endpoint
    r = client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=superuser_token_headers,
        json=data,
    )
    # Assert successful response and correct message
    assert r.status_code == 200
    assert r.json() == {"message": "Password updated successfully"}
    # Verify password change in database
    user = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert user
    assert verify_password(data["new_password"], user.hashed_password)
    # Revert the password back to FIRST_SUPERUSER_PASSWORD so the other tests can continue to run
    revert_token = generate_password_reset_token(email=settings.FIRST_SUPERUSER)
    revert_data = {
        "new_password": settings.FIRST_SUPERUSER_PASSWORD,
        "token": revert_token,
    }
    revert_r = client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=superuser_token_headers,
        json=revert_data,
    )
    # Assert successful revert
    assert revert_r.status_code == 200
    assert revert_r.json() == {"message": "Password updated successfully"}


@mark.order("last")
def test_reset_password_invalid_token(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test the reset password endpoint with an invalid token.

    This function tests the API's response when attempting to reset
    a password with an invalid token.

    Args:
        client (TestClient): The test client for making HTTP requests.
        superuser_token_headers (dict[str, str]): Headers containing the superuser's authentication token.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    Notes:
        This test prepares reset password data with an invalid token,
        sends a POST request to the reset password endpoint, and verifies
        that the API returns a bad request response with the correct error message.
    """
    # Prepare reset password data with invalid token
    data = {"new_password": "changethis", "token": "invalid"}
    # Send POST request to reset password endpoint
    r = client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=superuser_token_headers,
        json=data,
    )
    response = r.json()
    # Assert bad request response and correct error message
    assert "detail" in response
    assert r.status_code == 400
    assert response["detail"] == "Invalid token"


@mark.order("last")
def test_reset_password_user_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test the reset password endpoint with a non-existent user.

    This function tests the API's response when attempting to reset
    the password for a user that does not exist in the system.

    Args:
        client (TestClient): The test client for making HTTP requests.
        superuser_token_headers (dict[str, str]): Headers containing the superuser's authentication token.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    Notes:
        This test generates a token for a non-existent user, sends a POST request
        to the reset password endpoint, and verifies that the API returns a not found
        response with the correct error message.
    """
    # Generate token for non-existent user
    token = generate_password_reset_token(email="this_email_does_not_exist@example.com")
    data = {"new_password": "changethis", "token": token}
    # Send POST request to reset password endpoint
    r = client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=superuser_token_headers,
        json=data,
    )
    # Assert not found response and correct error message
    assert r.status_code == 404
    assert (
        r.json()["detail"] == "The user with this email does not exist in the system."
    )


@mark.order("last")
def test_reset_password_expired_token(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test the reset password endpoint with an expired token.

    This function tests the API's response when attempting to reset
    a password with an expired token.

    Args:
        client (TestClient): The test client for making HTTP requests.
        superuser_token_headers (dict[str, str]): Headers containing the superuser's authentication token.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    Notes:
        This test mocks the verify_password_reset_token function to simulate an expired token,
        sends a POST request to the reset password endpoint, and verifies that the API
        returns a bad request response with the correct error message.
    """
    # Mock verify_password_reset_token to return None (simulating expired token)
    with patch("app.utils.verify_password_reset_token", return_value=None):
        data = {"new_password": "changethis", "token": "expired_token"}
        # Send POST request to reset password endpoint
        r = client.post(
            f"{settings.API_V1_STR}/reset-password/",
            headers=superuser_token_headers,
            json=data,
        )
        # Assert bad request response and correct error message
        assert r.status_code == 400
        assert r.json()["detail"] == "Invalid token"


@mark.order("last")
def test_reset_password_inactive_user(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test the reset password endpoint with an inactive user.

    This function tests the API's response when attempting to reset
    the password for an inactive user.

    Args:
        client (TestClient): The test client for making HTTP requests.
        superuser_token_headers (dict[str, str]): Headers containing the superuser's authentication token.
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    Notes:
        This test creates an inactive user, generates a token for this user,
        sends a POST request to the reset password endpoint, and verifies that
        the API returns a bad request response with the correct error message.
    """
    # Create an inactive user
    user_in = UserCreate(
        email=random_email(),
        password="password1234!",
        is_active=False,
    )
    user = crud.create_user(session=db, user_create=user_in)
    # Generate token for inactive user
    token = generate_password_reset_token(email=user.email)
    data = {"new_password": user_in.password, "token": token}
    # Send POST request to reset password endpoint
    r = client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=superuser_token_headers,
        json=data,
    )
    # Assert bad request response and correct error message
    assert r.status_code == 400
    assert r.json()["detail"] == "Inactive user"


@mark.order("last")
def test_recover_password_html_content(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test the recover password html content endpoint.

    This function tests the API endpoint for retrieving the HTML content
    for password recovery.

    Args:
        client (TestClient): The test client for making HTTP requests.
        superuser_token_headers (dict[str, str]): Headers containing the superuser's authentication token.
        db (Session): The database session.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    Notes:
        This test creates a test user, sends a POST request to the password recovery
        HTML content endpoint, and verifies that the response is successful and
        contains the expected content type and headers.
    """
    # Create a test user
    user_in = UserCreate(
        email=random_email(),
        password="password1234!",
        is_active=True,
    )
    user = crud.create_user(session=db, user_create=user_in)
    # Send POST request to password recovery HTML content endpoint
    response = client.post(
        f"{settings.API_V1_STR}/password-recovery-html-content/{user.email}",
        headers=superuser_token_headers,
    )
    # Assert successful response and correct content type
    assert response.status_code == 200
    assert response.headers.get("content-type") == "text/html; charset=utf-8"
    assert "subject:" in response.headers
    # assert "Reset your password" in response.text


@mark.order("last")
def test_recover_password_html_content_user_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test the recover password html content endpoint with a non-existent user.

    This function tests the API's response when attempting to retrieve
    the password recovery HTML content for a user that does not exist in the system.

    Args:
        client (TestClient): The test client for making HTTP requests.
        superuser_token_headers (dict[str, str]): Headers containing the superuser's authentication token.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    Notes:
        This test sends a POST request to the password recovery HTML content endpoint
        with a non-existent email, and verifies that the API returns a not found
        response with the correct error message.
    """
    # Send POST request to password recovery HTML content endpoint with non-existent email
    response = client.post(
        f"{settings.API_V1_STR}/password-recovery-html-content/this_email_does_not_exist@example.com",
        headers=superuser_token_headers,
    )
    # Assert not found response and correct error message
    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == "The user with this username does not exist in the system."
    )


@mark.order("last")
def test_recover_password_html_content_not_superuser(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test the recover password html content endpoint with a normal user.

    This function tests the API's response when a normal user attempts to
    retrieve the password recovery HTML content.

    Args:
        client (TestClient): The test client for making HTTP requests.
        normal_user_token_headers (dict[str, str]): Headers containing a normal user's authentication token.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    Notes:
        This test sends a POST request to the password recovery HTML content endpoint
        with a normal user's token, and verifies that the API returns a forbidden
        response with the correct error message.
    """
    # Send POST request to password recovery HTML content endpoint with normal user token
    response = client.post(
        f"{settings.API_V1_STR}/password-recovery-html-content/{random_email()}",
        headers=normal_user_token_headers,
    )
    # Assert forbidden response and correct error message
    assert response.status_code == 403
    assert response.json()["detail"] == "The user doesn't have enough privileges"
