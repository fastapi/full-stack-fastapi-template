import secrets
import warnings
from typing import Annotated, Any, Dict, Literal, Optional

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    Field,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
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
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

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

    # PostgreSQL settings
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

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

    # MongoDB settings
    MONGODB_SERVER: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_USER: str = ""
    MONGODB_PASSWORD: str = ""
    MONGODB_DB: str = "political_social_media"
    MONGODB_AUTH_SOURCE: str = "admin"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def MONGODB_URI(self) -> str:
        auth_part = ""
        if self.MONGODB_USER and self.MONGODB_PASSWORD:
            auth_part = f"{self.MONGODB_USER}:{self.MONGODB_PASSWORD}@"
        
        auth_source = f"?authSource={self.MONGODB_AUTH_SOURCE}" if auth_part else ""
        return f"mongodb://{auth_part}{self.MONGODB_SERVER}:{self.MONGODB_PORT}/{self.MONGODB_DB}{auth_source}"

    # Redis settings
    REDIS_SERVER: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    @computed_field  # type: ignore[prop-decorator]
    @property
    def REDIS_URI(self) -> str:
        auth_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth_part}{self.REDIS_SERVER}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Pinecone (Vector Database) settings
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "us-west1-gcp"
    PINECONE_INDEX_NAME: str = "political-content"

    # Celery settings
    CELERY_BROKER: str = "amqp://guest:guest@localhost:5672//"
    CELERY_RESULT_BACKEND: str = ""  # Will default to Redis URI if not set
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: list[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    CELERY_TASK_ROUTES: Dict[str, Dict[str, str]] = {
        "app.tasks.scraping.*": {"queue": "scraping"},
        "app.tasks.analysis.*": {"queue": "analysis"},
        "app.tasks.notifications.*": {"queue": "notifications"},
    }

    @computed_field  # type: ignore[prop-decorator]
    @property
    def celery_result_backend_uri(self) -> str:
        """Return Redis URI as the default Celery result backend if none specified."""
        return self.CELERY_RESULT_BACKEND or self.REDIS_URI
    
    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_CONSUMER_GROUP_ID: str = "political-media-analysis"
    KAFKA_TOPIC_SOCIAL_MEDIA_POSTS: str = "social-media-posts"
    KAFKA_TOPIC_SENTIMENT_ANALYSIS: str = "sentiment-analysis"
    KAFKA_TOPIC_ENTITY_RECOGNITION: str = "entity-recognition"
    
    # NLP model settings
    SPACY_MODEL_NAME: str = "en_core_web_lg"
    TRANSFORMER_MODEL_NAME: str = "distilbert-base-uncased"
    SENTENCE_TRANSFORMER_MODEL_NAME: str = "all-MiniLM-L6-v2"
    
    # Email settings
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
        """Check if a secret is using a default value and warn the user."""
        if value is not None and value in {"changethis", "changeme", ""}:
            message = f"The value of {var_name} is \"{value}\", for security, please change it, at least for deployments."
            warnings.warn(message, stacklevel=1)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        """Enforce that secrets don't use default values."""
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret("MONGODB_PASSWORD", self.MONGODB_PASSWORD)
        self._check_default_secret("REDIS_PASSWORD", self.REDIS_PASSWORD)
        self._check_default_secret("PINECONE_API_KEY", self.PINECONE_API_KEY)
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD)
        return self


settings = Settings()  # type: ignore
