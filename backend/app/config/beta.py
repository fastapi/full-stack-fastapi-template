from pydantic_settings import SettingsConfigDict
from app.config.base import BaseConfig


class BetaConfig(BaseConfig):
    """Beta/Staging environment configuration"""

    environment: str = "beta"
    debug: bool = True  # Still debug but less verbose

    # Database
    pg_database: str = "ai_prompts_beta"
    pg_pool_size: int = 10

    # Logging
    log_level: str = "INFO"

    # CORS - Restrict to beta domain
    allowed_origins: list[str] = [
        "https://beta.yourapp.com",
        "https://staging.yourapp.com"
    ]

    # Rate limiting - Moderate limits
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 200
    rate_limit_period: int = 60

    # Security - Use real secrets from env
    # secret_key loaded from .env.beta

    model_config = SettingsConfigDict(
        env_file=".env.beta",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
