import secrets
import warnings
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    """
    Parse CORS settings.

    This function parses the CORS settings from various input formats.
    It's not protected and can be used by any part of the application.

    Args:
        v (Any): The input value to parse.

    Returns:
        list[str] | str: Parsed CORS settings.

    Raises:
        ValueError: If the input cannot be parsed.

    Notes:
        Accepts comma-separated string or list of strings.
    """
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    # Configuration for the settings model
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # API version string
    API_V1_STR: str = "/api/v1"
    # Secret key for security (default is a random URL-safe string)
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # Token expiration time (8 days)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # Frontend host URL
    FRONTEND_HOST: str = "http://localhost:5173"
    # Current environment (local, staging, production)
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    # CORS origins configuration
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        """
        Get all CORS origins.

        This property computes and returns all CORS origins including the frontend host.
        It's not protected and can be accessed by any part of the application.

        Args:
            None

        Returns:
            list[str]: List of all CORS origins.

        Raises:
            None

        Notes:
            Combines backend CORS origins with the frontend host.
        """
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    # Project name
    PROJECT_NAME: str
    # Sentry DSN for error tracking
    SENTRY_DSN: HttpUrl | None = None

    # Database configuration
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        """
        Get SQLAlchemy database URI.

        This property computes and returns the SQLAlchemy database URI.
        It's not protected and can be accessed by any part of the application.

        Args:
            None

        Returns:
            PostgresDsn: The SQLAlchemy database URI.

        Raises:
            None

        Notes:
            Constructs the URI using the PostgreSQL configuration settings.
        """
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    # Email configuration
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    # TODO: update type to EmailStr when sqlmodel supports it
    EMAILS_FROM_EMAIL: str | None = None
    EMAILS_FROM_NAME: str | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        """
        Set default email sender name.

        This method sets the default email sender name if not provided.
        It's not protected and is used internally by the Settings class.

        Args:
            None

        Returns:
            Self: The Settings instance.

        Raises:
            None

        Notes:
            Uses the project name as the default sender name.
        """
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    # Password reset token expiration time
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        """
        Check if emails are enabled.

        This property determines if the email functionality is enabled.
        It's not protected and can be accessed by any part of the application.

        Args:
            None

        Returns:
            bool: True if emails are enabled, False otherwise.

        Raises:
            None

        Notes:
            Emails are considered enabled if SMTP host and sender email are set.
        """
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    # TODO: update type to EmailStr when sqlmodel supports it
    EMAIL_TEST_USER: str = "test@example.com"
    # TODO: update type to EmailStr when sqlmodel supports it
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        """
        Check for default secret values.

        This method checks if a secret value is set to its default and raises a warning or error.
        It's not protected and is used internally by the Settings class.

        Args:
            var_name (str): The name of the variable being checked.
            value (str | None): The value of the variable.

        Returns:
            None

        Raises:
            ValueError: If the value is "changethis" in non-local environments.

        Notes:
            Warns in local environment, raises error in other environments.
        """
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        """
        Enforce non-default secrets.

        This method ensures that secret values are not left as their defaults.
        It's not protected and is used internally by the Settings class.

        Args:
            None

        Returns:
            Self: The Settings instance.

        Raises:
            ValueError: If any secret is left as its default value.

        Notes:
            Checks SECRET_KEY, POSTGRES_PASSWORD, and FIRST_SUPERUSER_PASSWORD.
        """
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self


# Create an instance of the Settings class
settings = Settings()  # type: ignore
