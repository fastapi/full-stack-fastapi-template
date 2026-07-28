from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # `model_` is a reserved pydantic namespace; we use MODEL_PATH because it
    # matches how the rest of the stack names things.
    model_config = SettingsConfigDict(protected_namespaces=(), extra="ignore")

    MODEL_PATH: str = "/data/aimodels/LaBSE"

    # Placement. FORCE_CPU mirrors the flag the workbench backend already uses.
    FORCE_CPU: bool = False

    # fp16 halves resident weights and speeds up the forward pass, but it is a
    # numerical change. Defaults off so this service is a drop-in replacement
    # for the in-process model; turn it on only after comparing scores.
    FP16: bool = False

    # Throughput knob. sentence-transformers sorts each call by length before
    # batching, so the padding win is automatic — this controls how much work
    # rides on each forward pass.
    BATCH_SIZE: int = 64

    # Refuse absurd payloads rather than OOM the GPU mid-batch.
    MAX_TEXTS_PER_REQUEST: int = 8192

    # /v1/align cannot be chunked — kNN is global over the corpus — so it gets
    # its own ceiling, per side. 100k x 768 float32 is ~300 MB of vectors plus
    # the faiss index; exact search at that size is minutes of CPU. Raise it
    # only alongside use_ann.
    MAX_ALIGN_TEXTS_PER_SIDE: int = 100_000

    # One GPU means one batch at a time. Callers get concurrency by being many;
    # this service gets throughput by batching, not by parallel forward passes.
    MAX_CONCURRENT_BATCHES: int = 1

    # Run one tiny encode after load so the first real request doesn't pay for
    # CUDA kernel autotuning.
    WARMUP: bool = True


settings = Settings()
