from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class BaseConfig(BaseSettings):
    """Base configuration shared across all environments"""

    # Application Info
    app_name: str = "Kila E-Commerce Intelligence"
    app_version: str = "1.0.0"

    # Environment
    environment: str = "development"
    debug: bool = True

    # API Settings
    api_prefix: str = "/api/v1"
    allowed_origins: list[str] = ["*"]

    # Database Settings (PostgreSQL)
    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_user: str = "yongzhang"
    pg_password: str = ""
    pg_database: str = "kila_intelligence"
    pg_pool_size: int = 10
    pg_max_overflow: int = 20

    # JWT settings
    algorithm: str = "HS256"
    access_token_expires_minutes: int = 60
    refresh_token_expires_days: int = 7

    # Email (optional, for verification)
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None

    # AI Model Settings
    ai_model_url: str = "http://localhost:11434"
    ai_model_api_key: str = ''
    ai_model: str = "qwen3-coder:30b"
    max_tokens: int = 1024 * 1024
    ai_timeout: int = 30  # seconds

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    api_key_header: str = "X-API-Key"

    # Clerk
    clerk_secret_key: str = ""
    clerk_publishable_key: str = ""
    clerk_jwks_url: str = "https://cuddly-reindeer-57.clerk.accounts.dev/.well-known/jwks.json"

    # Stripe
    stripe_webhook_secret: str = ""
    stripe_pro_price_id: str = ""
    stripe_secret_key: str = ""
    stripe_frontend_url: str = "http://localhost:3000"

    # Rate Limiting
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds

    # Report storage
    report_storage_backend: str = "local"
    report_storage_path: str = "/app/storage/reports"

    # Computed Properties
    @property
    def database_url(self) -> str:
        password_part = f":{self.pg_password}" if self.pg_password else ""
        return f"postgresql+asyncpg://{self.pg_user}{password_part}@{self.pg_host}:{self.pg_port}/{self.pg_database}"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields in .env
    )
