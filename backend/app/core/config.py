import json
import warnings
from typing import Annotated, Any, Literal

from pydantic import AnyUrl, BeforeValidator, SecretStr, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and v.startswith("["):
        return json.loads(v)
    if isinstance(v, str):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
        frozen=True,
    )

    # Required fields — no defaults; must come from environment
    SUPABASE_URL: AnyUrl
    SUPABASE_SERVICE_KEY: SecretStr
    CLERK_SECRET_KEY: SecretStr

    # Optional fields with defaults
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    SERVICE_NAME: str = "my-service"
    SERVICE_VERSION: str = "0.1.0"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: Annotated[list[str] | str, BeforeValidator(parse_cors)] = []
    WITH_UI: bool = False
    CLERK_JWKS_URL: str | None = None
    CLERK_AUTHORIZED_PARTIES: list[str] = []
    GIT_COMMIT: str = "unknown"
    BUILD_TIME: str = "unknown"
    HTTP_CLIENT_TIMEOUT: int = 30
    HTTP_CLIENT_MAX_RETRIES: int = 3
    SENTRY_DSN: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]

    def _check_default_secret(
        self, var_name: str, value: str | SecretStr | None
    ) -> None:
        secret_value: str | None
        if isinstance(value, SecretStr):
            secret_value = value.get_secret_value()
        else:
            secret_value = value

        if secret_value == "changethis":
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
        self._check_default_secret("SUPABASE_SERVICE_KEY", self.SUPABASE_SERVICE_KEY)
        self._check_default_secret("CLERK_SECRET_KEY", self.CLERK_SECRET_KEY)

        if self.ENVIRONMENT == "production":
            cors_list = self.BACKEND_CORS_ORIGINS
            if isinstance(cors_list, str):
                origins = [cors_list]
            else:
                origins = [str(o) for o in cors_list]
            if "*" in origins:
                raise ValueError(
                    "wildcard CORS origin ('*') is not allowed in production"
                )

        return self


settings = Settings()  # type: ignore
