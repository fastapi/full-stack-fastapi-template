import secrets
import warnings
from typing import Any, Annotated, Literal

from pydantic import AnyUrl, BeforeValidator, EmailStr, HttpUrl, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self
from pydantic import AnyUrl, HttpUrl, EmailStr


def parse_cors(v: Any) -> list[str] | str:
    """Parses CORS origins from env or defaults."""
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    """
    Application settings (no .env required).
    Uses SQLite instead of PostgreSQL.
    """

    model_config = SettingsConfigDict(
        env_ignore_empty=True,
        extra="ignore",
    )

    # --- Core app settings ---
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "My SQLite App"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    SENTRY_DSN: HttpUrl | None = None  # ✅ Added this line


    # --- CORS ---
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        """Combine backend and frontend origins for CORS."""
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    # --- Database (SQLite only) ---
    SQLITE_DB_PATH: str = "./app.db"

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """SQLAlchemy connection string for SQLite."""
        return f"sqlite:///{self.SQLITE_DB_PATH}"

    # --- Email (optional) ---
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

    @computed_field
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    # --- Superuser ---
    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "changeme"

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changeme":
            message = f'The value of {var_name} is "changeme", please change it.'
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD)
        return self


# Instantiate settings immediately
settings = Settings()  # type: ignore
