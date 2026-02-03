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

    # Database Settings (common structure)
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "kila_intelligence"
    mysql_pool_size: int = 10
    mysql_max_overflow: int = 20

    # JWT settings
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expires_minutes: int = 60
    refresh_token_expires_days: int = 7

    # Email (optional, for verification)
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None

    # Database tables setting
    db_companies_table_name: str = "companies"
    db_users_table_name: str = "users"
    db_users_profile_table_name: str = "users_profile"
    db_users_security_table_name: str = "users_security"
    db_users_session_table_name: str = "users_session"
    db_brand_prompts_table_name: str = "brand_prompts"
    db_projects_table_name: str = "projects"

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

    # Rate Limiting
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds

    # Computed Properties
    @property
    def database_url(self) -> str:
        return f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"

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
