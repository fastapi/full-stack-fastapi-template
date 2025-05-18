"""
Application configuration.

This module provides a centralized configuration system for the application,
organized by feature modules.
"""
import logging
import secrets
import warnings
from typing import Annotated, Any, Dict, List, Literal, Optional

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> List[str] | str:
    """Parse CORS settings from string to list."""
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class DatabaseSettings(BaseSettings):
    """Database-specific settings."""
    
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        """Build the database URI."""
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


class SecuritySettings(BaseSettings):
    """Security-specific settings."""
    
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Superuser account for initialization
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str


class EmailSettings(BaseSettings):
    """Email-specific settings."""
    
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEST_USER: EmailStr = "test@example.com"

    @computed_field
    @property
    def emails_enabled(self) -> bool:
        """Check if email functionality is enabled."""
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)


class ApplicationSettings(BaseSettings):
    """Application-wide settings."""
    
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    LOG_LEVEL: str = "INFO"
    FRONTEND_HOST: str = "http://localhost:5173"
    SENTRY_DSN: Optional[HttpUrl] = None
    
    BACKEND_CORS_ORIGINS: Annotated[
        List[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field
    @property
    def all_cors_origins(self) -> List[str]:
        """Get all allowed CORS origins including frontend host."""
        origins = [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]
        if self.FRONTEND_HOST not in origins:
            origins.append(self.FRONTEND_HOST)
        return origins


class Settings(ApplicationSettings, SecuritySettings, DatabaseSettings, EmailSettings):
    """
    Combined settings from all modules.
    
    This class combines settings from all feature modules and provides
    validation methods.
    """
    
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        """Set default email sender name if not provided."""
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        """Check if a secret value is still set to default."""
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
        """Enforce that secrets are not left at default values."""
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )
        return self
    
    def get_module_settings(self, module_name: str) -> Dict[str, Any]:
        """
        Get settings for a specific module.
        
        This method allows modules to access only the settings relevant to them.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Dictionary of module-specific settings
        """
        if module_name == "auth":
            # Auth module settings
            return {
                "secret_key": self.SECRET_KEY,
                "access_token_expire_minutes": self.ACCESS_TOKEN_EXPIRE_MINUTES,
            }
        elif module_name == "email":
            # Email module settings
            return {
                "smtp_tls": self.SMTP_TLS,
                "smtp_ssl": self.SMTP_SSL,
                "smtp_port": self.SMTP_PORT,
                "smtp_host": self.SMTP_HOST,
                "smtp_user": self.SMTP_USER,
                "smtp_password": self.SMTP_PASSWORD,
                "emails_from_email": self.EMAILS_FROM_EMAIL,
                "emails_from_name": self.EMAILS_FROM_NAME,
                "email_reset_token_expire_hours": self.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
                "emails_enabled": self.emails_enabled,
            }
        elif module_name == "users":
            # Users module settings
            return {
                "first_superuser": self.FIRST_SUPERUSER,
                "first_superuser_password": self.FIRST_SUPERUSER_PASSWORD,
            }
        
        # Default to returning empty dict for unknown modules
        return {}


# Initialize settings
settings = Settings()