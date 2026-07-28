from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(protected_namespaces=(), extra="ignore")

    # This service serves any COMET checkpoint. CometKiwi (reference-free) and
    # wmt22-comet-da (reference-based) resolve to byte-identical dependency
    # trees, so they share one image and differ only by MODEL_PATH at deploy
    # time. Splitting them into separate images would duplicate, not isolate.
    MODEL_PATH: str = "/data/aimodels/huggingface/checkpoints/model.ckpt"

    # Reported in responses and /v1/info so callers can tell the deployments
    # apart. Set per deployment: "comekiwi" or "comet".
    MODEL_NAME: str = "comet"

    FORCE_CPU: bool = False

    # Caps peak activation memory regardless of request size. The backend
    # scored whole requests in one forward pass, which is fine at 32 rows and
    # not fine at 4000.
    BATCH_SIZE: int = 32

    MAX_ROWS_PER_REQUEST: int = 4096

    # One GPU, one forward pass at a time.
    MAX_CONCURRENT_BATCHES: int = 1

    WARMUP: bool = True


settings = Settings()
