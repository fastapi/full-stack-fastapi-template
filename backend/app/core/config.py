"""
Application configuration settings.

This module defines the application configuration using Pydantic settings management.
It loads environment variables from a .env file and provides type-safe access to them.
"""
import secrets
import warnings
from pathlib import Path
from typing import Annotated, Any, Literal, Optional, Union

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    field_validator,
    model_validator,
    RedisDsn,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent


def parse_cors(v: Any) -> list[str] | str:
    """Parse CORS origins from a comma-separated string or list."""
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError(v)


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    model_config = SettingsConfigDict(env_prefix="DATABASE_")
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "copilot"
    POSTGRES_PORT: int = 5432
    SQL_ECHO: bool = False
    
    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        """Generate the PostgreSQL database URI."""
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=f"/{self.POSTGRES_DB}",
        )
    
    @computed_field
    @property
    def ASYNC_SQLALCHEMY_DATABASE_URI(self) -> str:
        """Generate the async PostgreSQL database URI."""
        return str(
            MultiHostUrl.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=f"/{self.POSTGRES_DB}",
            )
        )


class AuthSettings(BaseSettings):
    """Authentication and authorization settings."""
    model_config = SettingsConfigDict(env_prefix="AUTH_")
    
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 24
    
    # First superuser
    FIRST_SUPERUSER: EmailStr = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "changeme"
    
    # OAuth2
    GOOGLE_OAUTH_CLIENT_ID: Optional[str] = None
    GOOGLE_OAUTH_CLIENT_SECRET: Optional[str] = None
    GOOGLE_OAUTH_REDIRECT_URI: Optional[HttpUrl] = None
    
    MICROSOFT_OAUTH_CLIENT_ID: Optional[str] = None
    MICROSOFT_OAUTH_CLIENT_SECRET: Optional[str] = None
    MICROSOFT_OAUTH_REDIRECT_URI: Optional[HttpUrl] = None
    MICROSOFT_OAUTH_TENANT: str = "common"
    
    # Session
    SESSION_SECRET_KEY: str = secrets.token_urlsafe(32)
    SESSION_COOKIE_NAME: str = "session"
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SECURE: bool = False  # Set to True in production with HTTPS
    SESSION_COOKIE_SAMESITE: str = "lax"
    SESSION_COOKIE_DOMAIN: Optional[str] = None
    
    # CORS
    BACKEND_CORS_ORIGINS: list[HttpUrl] = [
        HttpUrl("http://localhost:3000"),
        HttpUrl("http://localhost:8000"),
    ]
    
    @property
    def all_cors_origins(self) -> list[str]:
        """Get all allowed CORS origins."""
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]


class EmailSettings(BaseSettings):
    """Email configuration settings."""
    model_config = SettingsConfigDict(env_prefix="EMAIL_")
    
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    @property
    def EMAILS_ENABLED(self) -> bool:
        """Check if email sending is enabled."""
        return bool(self.SMTP_HOST and self.SMTP_USER and self.SMTP_PASSWORD)


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    model_config = SettingsConfigDict(env_prefix="REDIS_")
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_SSL: bool = False
    
    @computed_field
    @property
    def REDIS_URL(self) -> RedisDsn:
        """Generate the Redis URL."""
        return RedisDsn.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            username=None,
            password=self.REDIS_PASSWORD,
            path=f"/{self.REDIS_DB}",
        )


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(DatabaseSettings, AuthSettings, EmailSettings, RedisSettings):
    """Application settings."""
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
        case_sensitive=True,
    )
    
    # Application
    PROJECT_NAME: str = "Copilot API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    
    # Allow development as an alias for local
    @model_validator(mode='before')
    @classmethod
    def validate_environment(cls, data: Any) -> Any:
        if isinstance(data, dict) and data.get('ENVIRONMENT') == 'development':
            data['ENVIRONMENT'] = 'local'
        return data
    
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # API
    API_PREFIX: str = "/api"
    PROJECT_VERSION: str = "1.0.0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    LOG_FILE: Optional[Path] = None
    
    # Frontend
    FRONTEND_HOST: HttpUrl = "http://localhost:3000"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[AnyUrl] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # Rate limiting
    RATE_LIMIT: bool = True
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Security headers
    SECURITY_HEADERS: bool = True
    
    # Trusted hosts
    ALLOWED_HOSTS: list[str] = ["*"]
    
    # Application URLs
    @computed_field
    @property
    def BASE_URL(self) -> HttpUrl:
        """Get the base URL of the application."""
        if self.ENVIRONMENT == "production":
            return HttpUrl("https://api.copilot.example.com")
        elif self.ENVIRONMENT == "staging":
            return HttpUrl("https://staging-api.copilot.example.com")
        return HttpUrl("http://localhost:8000")
    
    @computed_field
    @property
    def FRONTEND_URL(self) -> HttpUrl:
        """Get the frontend URL."""
        if self.ENVIRONMENT == "production":
            return HttpUrl("https://copilot.example.com")
        elif self.ENVIRONMENT == "staging":
            return HttpUrl("https://staging.copilot.example.com")
        return HttpUrl("http://localhost:3000")
    
    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        """Get all allowed CORS origins."""
        origins = [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]
        origins.append(str(self.FRONTEND_URL).rstrip("/"))
        return list(set(origins))  # Remove duplicates
    
    @field_validator("ENVIRONMENT")
    def set_debug(cls, v: str) -> str:
        """Set DEBUG based on ENVIRONMENT."""
        import os
        os.environ["DEBUG"] = str(v == "local").lower()
        return v
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, list[Union[str, HttpUrl]]]) -> list[HttpUrl]:
        """Parse CORS origins from a comma-separated string or list."""
        if isinstance(v, str):
            if v.startswith("["):
                # Handle JSON array string
                import json
                v = json.loads(v)
            else:
                # Handle comma-separated string
                v = [i.strip() for i in v.split(",")]
        
        # Convert all items to HttpUrl objects
        result = []
        for item in v:
            if isinstance(item, str):
                result.append(HttpUrl(item))
            elif isinstance(item, HttpUrl):
                result.append(item)
            else:
                raise ValueError(f"Invalid CORS origin: {item}")
        return result
    
    PROJECT_NAME: str
    SENTRY_DSN: HttpUrl | None = None
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "copilot"
    POSTGRES_PORT: int = 5432
    
    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None

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
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self


# Initialize settings
settings = Settings()

# Configure logging based on settings
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
        "console": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {"handlers": ["console"], "level": settings.LOG_LEVEL},
        "uvicorn": {"level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"level": "INFO", "propagate": False},
        "sqlalchemy.engine": {"level": "WARNING"},
        "sqlalchemy.pool": {"level": "WARNING"},
    },
}

# Apply logging configuration
import logging.config
logging.config.dictConfig(logging_config)

# Set log level for all loggers
for logger_name in logging.root.manager.loggerDict:
    if logger_name in logging_config["loggers"]:
        logging.getLogger(logger_name).setLevel(
            logging_config["loggers"][logger_name].get("level", settings.LOG_LEVEL)
        )
    else:
        logging.getLogger(logger_name).setLevel(settings.LOG_LEVEL)
