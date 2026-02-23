from pydantic_settings import SettingsConfigDict
from app.config.base import BaseConfig


class ProductionConfig(BaseConfig):
    """Production environment configuration"""

    environment: str = "production"
    debug: bool = False

    # Database
    pg_database: str = "kila_intelligence"
    pg_pool_size: int = 20
    pg_max_overflow: int = 40

    # Logging - Only important stuff
    log_level: str = "WARNING"

    # CORS - Strict domain whitelist
    allowed_origins: list[str] = [
        "http://www.spekila.com",
        "https://www.spekila.com",
        "http://spekila.com",
        "https://spekila.com",
    ]

    # Rate limiting - Strict limits
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60

    # AI Settings - Production model
    ai_model: str = "qwen3-coder:30b"
    ai_timeout: int = 60  # Longer timeout in production

    # Security - Must be set in environment
    # These will raise validation errors if not provided
    secret_key: str  # No default - must be in .env.prod

    model_config = SettingsConfigDict(
        env_file=".env.prod",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
