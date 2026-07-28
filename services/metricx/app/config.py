from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(protected_namespaces=(), extra="ignore")

    MODEL_PATH: str = "/data/aimodels/metricx"

    # The local checkpoint ships no tokenizer files, so we fall back to the
    # mt5-xl tokenizer from the HF cache under HF_HOME.
    TOKENIZER_ID: str = "google/mt5-xl"

    FORCE_CPU: bool = False

    # Pinned bf16 on GPU so we never silently fall back to fp32, which would
    # double both weight and activation memory. Same choice the backend made.
    BF16: bool = True

    # Caps peak GPU activation memory regardless of request size.
    BATCH_SIZE: int = 8

    # 1536 is the XL/XXL default.
    MAX_LENGTH: int = 1536

    MAX_ROWS_PER_REQUEST: int = 2048

    MAX_CONCURRENT_BATCHES: int = 1

    WARMUP: bool = True


settings = Settings()
