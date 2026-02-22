from app.config.base import BaseConfig
from pydantic_settings import SettingsConfigDict


class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""

    environment: str = "development"
    debug: bool = True

    # Database
    pg_database: str = "kila_intelligence"
    pg_pool_size: int = 5

    # Logging - More verbose in dev
    log_level: str = "DEBUG"

    # CORS - Allow localhost in development
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Rate limiting - Disabled in dev
    rate_limit_enabled: bool = False

    # AI Model Settings
    ai_model_url: str = "http://localhost:11434"
    ai_model_api_key: str = ''
    ai_model: str = "qwen3-coder:30b"
    max_tokens: int = 1024 * 1024
    ai_timeout: int = 60 * 2  # seconds

    model_config = SettingsConfigDict(
        env_file=".env.development",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
