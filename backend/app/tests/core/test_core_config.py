import pytest
from pydantic import ValidationError

from app.core.config import Settings, parse_cors


def test_parse_cors() -> None:
    """
    Test CORS parsing functionality.

    This function tests that the parse_cors function successfully parses a string of origins.
    The function is not protected and does not require authentication.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
        ValueError: If an invalid input is provided to parse_cors.

    Notes:
        This test covers parsing of comma-separated strings, lists, and single origins.
        It also checks for proper error handling with invalid input.
    """
    # Test parsing a comma-separated string of origins
    assert parse_cors("http://localhost,https://example.com") == [
        "http://localhost",
        "https://example.com",
    ]

    # Test parsing a list of origins
    assert parse_cors(["http://localhost", "https://example.com"]) == [
        "http://localhost",
        "https://example.com",
    ]

    # Test parsing a single origin
    assert parse_cors("http://localhost") == ["http://localhost"]

    # Test that an invalid input raises a ValueError
    with pytest.raises(ValueError):
        parse_cors(123)


def test_settings_default_values() -> None:
    """
    Test default Settings initialization.

    This function tests that the Settings class successfully initializes with default values.
    The function is not protected and does not require authentication.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the test fails.

    Notes:
        This test creates a Settings instance with minimal required parameters and checks
        that default values are set correctly for various configuration options.
    """
    # Create a Settings instance with minimal required parameters
    settings = Settings(
        PROJECT_NAME="Test Project",
        POSTGRES_SERVER="localhost",
        POSTGRES_USER="postgres",
        FIRST_SUPERUSER="admin@example.com",
        FIRST_SUPERUSER_PASSWORD="password123",
    )

    # Assert that default values are set correctly
    assert settings.API_V1_STR == "/api/v1"
    assert len(settings.SECRET_KEY) >= 32  # Ensure SECRET_KEY is sufficiently long
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60 * 24 * 8  # 8 days
    assert settings.FRONTEND_HOST == "http://localhost:5173"
    assert settings.ENVIRONMENT == "local"


def test_settings_custom_values() -> None:
    """
    Test custom Settings initialization.

    This function tests that the Settings class successfully initializes with custom values.
    The function is not protected and does not require authentication.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the test fails.

    Notes:
        This test creates a Settings instance with custom values and checks
        that these values are correctly set for various configuration options.
    """
    # Define custom settings
    custom_settings = {
        "API_V1_STR": "/custom/api",
        "SECRET_KEY": "mysecretkey",
        "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
        "FRONTEND_HOST": "https://example.com",
        "ENVIRONMENT": "production",
        "PROJECT_NAME": "Test Project",
        "POSTGRES_SERVER": "db.example.com",
        "POSTGRES_USER": "testuser",
        "POSTGRES_PASSWORD": "testpass",
        "POSTGRES_DB": "testdb",
        "FIRST_SUPERUSER": "admin@example.com",
        "FIRST_SUPERUSER_PASSWORD": "adminpass",
    }

    # Create a Settings instance with custom values
    settings = Settings(**custom_settings)  # type: ignore

    # Assert that custom values are set correctly
    assert settings.API_V1_STR == "/custom/api"
    assert settings.SECRET_KEY == "mysecretkey"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert settings.FRONTEND_HOST == "https://example.com"
    assert settings.ENVIRONMENT == "production"
    assert settings.PROJECT_NAME == "Test Project"
    assert settings.POSTGRES_SERVER == "db.example.com"
    assert settings.POSTGRES_USER == "testuser"
    assert settings.POSTGRES_PASSWORD == "testpass"
    assert settings.POSTGRES_DB == "testdb"
    assert settings.FIRST_SUPERUSER == "admin@example.com"
    assert settings.FIRST_SUPERUSER_PASSWORD == "adminpass"


def test_settings_computed_fields() -> None:
    """
    Test computed fields in Settings.

    This function tests that the Settings class successfully initializes with custom values
    and correctly computes derived fields.
    The function is not protected and does not require authentication.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the test fails.

    Notes:
        This test focuses on computed fields like all_cors_origins and SQLALCHEMY_DATABASE_URI.
    """
    # Define custom settings
    custom_settings = {
        "BACKEND_CORS_ORIGINS": ["http://localhost", "https://example.com"],
        "FRONTEND_HOST": "http://frontend.com",
        "POSTGRES_SERVER": "db.example.com",
        "POSTGRES_USER": "testuser",
        "POSTGRES_PASSWORD": "testpass",
        "POSTGRES_DB": "testdb",
        "PROJECT_NAME": "Test Project",
        "FIRST_SUPERUSER": "admin@example.com",
        "FIRST_SUPERUSER_PASSWORD": "adminpass",
    }

    # Create a Settings instance with custom values
    settings = Settings(**custom_settings)  # type: ignore[arg-type]

    # Assert that computed fields are correct
    assert settings.all_cors_origins == [
        "http://localhost",
        "https://example.com",
        "http://frontend.com",
    ]
    assert (
        str(settings.SQLALCHEMY_DATABASE_URI)
        == "postgresql+psycopg://testuser:testpass@db.example.com:5432/testdb"
    )


def test_settings_email_configuration() -> None:
    """
    Test email configuration in Settings.

    This function tests that the Settings class successfully initializes with custom email configuration.
    The function is not protected and does not require authentication.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the test fails.

    Notes:
        This test focuses on email-related settings and checks if they are correctly set.
    """
    # Define custom settings with email configuration
    custom_settings = {
        "SMTP_TLS": True,
        "SMTP_PORT": 587,
        "SMTP_HOST": "smtp.example.com",
        "SMTP_USER": "user@example.com",
        "SMTP_PASSWORD": "password123",
        "EMAILS_FROM_EMAIL": "noreply@example.com",
        "PROJECT_NAME": "Test Project",
        "FIRST_SUPERUSER": "admin@example.com",
        "FIRST_SUPERUSER_PASSWORD": "adminpass",
        "POSTGRES_SERVER": "localhost",
        "POSTGRES_USER": "postgres",
    }

    # Create a Settings instance with custom email configuration
    settings = Settings(**custom_settings)  # type: ignore[arg-type]

    # Assert that email configuration is set correctly
    assert settings.SMTP_TLS is True
    assert settings.SMTP_PORT == 587
    assert settings.SMTP_HOST == "smtp.example.com"
    assert settings.SMTP_USER == "user@example.com"
    assert settings.SMTP_PASSWORD == "password123"
    assert settings.EMAILS_FROM_EMAIL == "noreply@example.com"
    assert settings.EMAILS_FROM_NAME == "Test Project"
    assert settings.emails_enabled is True


def test_settings_validation() -> None:
    """
    Test Settings validation.

    This function tests that the Settings class successfully validates the environment and configuration.
    The function is not protected and does not require authentication.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
        ValidationError: If invalid settings are provided.

    Notes:
        This test checks for proper validation of environment, POSTGRES_PORT, and BACKEND_CORS_ORIGINS.
    """
    # Test that an invalid environment raises a ValidationError
    with pytest.raises(ValidationError):
        Settings(
            ENVIRONMENT="invalid_environment",  # type: ignore[arg-type]
            PROJECT_NAME="Test Project",
            POSTGRES_SERVER="localhost",
            POSTGRES_USER="postgres",
            FIRST_SUPERUSER="admin@example.com",
            FIRST_SUPERUSER_PASSWORD="password123",
        )

    # Test that an invalid POSTGRES_PORT raises a ValidationError
    with pytest.raises(ValidationError):
        Settings(
            POSTGRES_PORT="not_an_integer",  # type: ignore[arg-type]
            PROJECT_NAME="Test Project",
            POSTGRES_SERVER="localhost",
            POSTGRES_USER="postgres",
            FIRST_SUPERUSER="admin@example.com",
            FIRST_SUPERUSER_PASSWORD="password123",
        )

    # Test that an invalid BACKEND_CORS_ORIGINS raises a ValidationError
    with pytest.raises(ValidationError):
        Settings(
            BACKEND_CORS_ORIGINS="not_a_valid_url",
            PROJECT_NAME="Test Project",
            POSTGRES_SERVER="localhost",
            POSTGRES_USER="postgres",
            FIRST_SUPERUSER="admin@example.com",
            FIRST_SUPERUSER_PASSWORD="password123",
        )


def test_settings_default_secrets_warning() -> None:
    """
    Test default secrets warning in Settings.

    This function tests that the Settings class raises a warning when default secrets are used in a non-production environment.
    The function is not protected and does not require authentication.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the test fails.

    Notes:
        This test checks for a UserWarning when default secrets are used in a non-production environment.
    """
    # Test that using default secrets in non-production environment raises a warning
    with pytest.warns(UserWarning):
        Settings(
            SECRET_KEY="changethis",
            POSTGRES_PASSWORD="changethis",
            FIRST_SUPERUSER_PASSWORD="changethis",
            PROJECT_NAME="Test",
            FIRST_SUPERUSER="admin@example.com",
            POSTGRES_SERVER="localhost",
            POSTGRES_USER="postgres",
        )


def test_settings_default_secrets_error() -> None:
    """
    Test default secrets error in Settings.

    This function tests that the Settings class raises an error when default secrets are used in a production environment.
    The function is not protected and does not require authentication.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the test fails.
        ValueError: If default secrets are used in a production environment.

    Notes:
        This test checks for a ValueError when default secrets are used in a production environment.
    """
    # Test that using default secrets in production environment raises a ValueError
    with pytest.raises(ValueError):
        Settings(
            SECRET_KEY="changethis",
            POSTGRES_PASSWORD="changethis",
            FIRST_SUPERUSER_PASSWORD="changethis",
            ENVIRONMENT="production",
            PROJECT_NAME="Test",
            FIRST_SUPERUSER="admin@example.com",
            POSTGRES_SERVER="localhost",
            POSTGRES_USER="postgres",
        )
