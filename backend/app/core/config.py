import secrets
import warnings
from typing import Annotated, Any, Literal, Optional, List, Dict, Union

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
import secrets
import warnings
from typing import Annotated, Any, Literal, Optional, List

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
    AnyHttpUrl,
    validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self
from functools import lru_cache
import os
from pathlib import Path

# Obtener la ruta al directorio raíz del proyecto (Genius-INDUSTRIES)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"  # Permitir campos extra en el archivo .env
    )

    # Domain
    DOMAIN: str
    FRONTEND_HOST: str
    ENVIRONMENT: str

    # Project Info
    PROJECT_NAME: str
    STACK_NAME: str
    VERSION: str
    API_V1_STR: str

    # Backend
    BACKEND_CORS_ORIGINS: str = "http://localhost,http://localhost:5173,https://localhost,https://localhost:5173"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520

    # Nhost
    NHOST_URL: str
    NHOST_ADMIN_SECRET: str

    # Postgres
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # Database
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Storage
    STORAGE_BUCKET: str

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Feature Flags
    ENABLE_DOCS: bool = True
    ENABLE_TEST_ROUTE: bool = True

    # Sentry
    SENTRY_DSN: Optional[str] = None

    # Docker Images
    DOCKER_IMAGE_BACKEND: str
    DOCKER_IMAGE_FRONTEND: str

    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]

    @validator("ENABLE_DOCS", "ENABLE_TEST_ROUTE", pre=True)
    def parse_bool(cls, v: str) -> bool:
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return bool(v)

    @validator("POSTGRES_PORT", pre=True)
    def parse_port(cls, v: str) -> int:
        if isinstance(v, str):
            return int(v)
        return v

    # Configuración de seguridad
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

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
        self._check_default_secret("NHOST_ADMIN_SECRET", self.NHOST_ADMIN_SECRET)
        return self


@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
