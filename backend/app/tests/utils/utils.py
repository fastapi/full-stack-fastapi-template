import random
import string

from fastapi.testclient import TestClient

from app.core.config import settings


def random_lower_string() -> str:
    """
    Generate a random lowercase string.

    This function creates and returns a random string of 32 lowercase ASCII characters.

    Args:
        None

    Returns:
        str: A random string of 32 lowercase ASCII characters.

    Raises:
        None

    Notes:
        This function uses the random.choices method to select characters from string.ascii_lowercase.
    """
    # Generate a random string of 32 lowercase ASCII characters
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    """
    Generate a random email address.

    This function creates a random email address by combining two random lowercase strings.

    Args:
        None

    Returns:
        str: A randomly generated email address.

    Raises:
        None

    Notes:
        This function uses the random_lower_string function to generate the local and domain parts of the email.
    """
    # Create a random email by combining two random lowercase strings
    return f"{random_lower_string()}@{random_lower_string()}.com"


def get_superuser_token_headers(client: TestClient) -> dict[str, str]:
    """
    Get authentication token headers for the superuser.

    This function obtains an access token for the superuser and returns it in the format required for authorization headers.

    Args:
        client (TestClient): The test client used to make requests.

    Returns:
        dict[str, str]: A dictionary containing the authorization header with the access token.

    Raises:
        ValueError: If no access token is found in the response.

    Notes:
        This function uses the settings module to get the superuser credentials and API endpoint.
    """
    # Prepare login data for the superuser
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    # Send a POST request to obtain an access token
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    # Parse the JSON response
    tokens = r.json()
    # Extract the access token from the response
    a_token = tokens.get("access_token")
    # Raise an error if no access token is found
    if not a_token:
        raise ValueError(f"No access token found in response: {tokens}")
    # Return the token in the format required for authorization headers
    return {"Authorization": f"Bearer {a_token}"}
