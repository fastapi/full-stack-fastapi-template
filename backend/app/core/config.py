import secrets
import warnings
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "testing", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    PROJECT_NAME: str
    SENTRY_DSN: HttpUrl | None = None

    # Supabase Configuration
    # Use DATABASE_URL with Supabase pooler connection for IPv6 compatibility
    # Allows SQLite for testing (sqlite:///) and PostgreSQL for production
    DATABASE_URL: PostgresDsn | str
    SUPABASE_URL: HttpUrl
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_STORAGE_BUCKET_WORKSHEETS: str = "worksheets"

    # Legacy Postgres fields - deprecated, kept for backward compatibility
    # Use DATABASE_URL instead
    POSTGRES_SERVER: str | None = None
    POSTGRES_PORT: int | None = 5432
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn | str:
        # Use DATABASE_URL directly (Supabase pooler connection)
        # In testing, this may be a SQLite URL (sqlite:///)
        return self.DATABASE_URL

    # Redis and Celery Configuration
    REDIS_PASSWORD: str
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Mistral OCR Configuration
    MISTRAL_API_KEY: str | None = None
    OCR_PROVIDER: str = "mistral"
    OCR_MAX_RETRIES: int = 3
    OCR_RETRY_DELAY: int = 2  # seconds (exponential backoff base)
    OCR_MAX_PAGES: int = 50  # reject documents >50 pages

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: EmailStr | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
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
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("REDIS_PASSWORD", self.REDIS_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self

    @model_validator(mode="after")
    def _validate_mistral_api_key(self) -> Self:
        """Validate MISTRAL_API_KEY is set in production environments."""
        if self.ENVIRONMENT in ["production", "staging"]:
            if not self.MISTRAL_API_KEY:
                raise ValueError(
                    "MISTRAL_API_KEY must be set in production/staging environments"
                )
        return self

    @model_validator(mode="after")
    def _validate_database_url(self) -> Self:
        """Validate DATABASE_URL based on environment.

        - Production/Staging: Must be PostgreSQL
        - Local/Testing: Allows SQLite for fast testing
        """
        db_url = str(self.DATABASE_URL)

        # Allow SQLite for testing (sqlite:///)
        if db_url.startswith("sqlite"):
            return self

        # For production/staging, ensure it's PostgreSQL
        if self.ENVIRONMENT in ["staging", "production"]:
            if not any(
                db_url.startswith(scheme)
                for scheme in [
                    "postgres://",
                    "postgresql://",
                    "postgresql+psycopg://",
                    "postgresql+asyncpg://",
                    "postgresql+pg8000://",
                ]
            ):
                raise ValueError(
                    f"DATABASE_URL must be PostgreSQL in {self.ENVIRONMENT} environment"
                )

        return self


settings = Settings()  # type: ignore
