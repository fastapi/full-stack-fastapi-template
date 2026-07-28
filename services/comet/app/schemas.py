from pydantic import BaseModel, Field


class Row(BaseModel):
    src: str  # Source text
    mt: str   # Machine translation
    # Reference-based checkpoints (wmt22-comet-da) require this; reference-free
    # ones (CometKiwi) do not take it. Dropped from the payload entirely when
    # None, so a reference-free model sees exactly the {src, mt} it expects.
    ref: str | None = None


class ScoreRequest(BaseModel):
    rows: list[Row] = Field(..., min_length=1)


class ScoreResponse(BaseModel):
    model: str
    count: int

    # Full precision — rounding is the caller's presentation concern.
    scores: list[float]
    system_score: float


class InfoResponse(BaseModel):
    model: str
    ready: bool
    device: str
    model_path: str
    batch_size: int
    max_rows_per_request: int
    error: str | None = None
