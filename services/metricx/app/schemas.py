from pydantic import BaseModel, Field


class Row(BaseModel):
    # MetricX runs reference-free when ref is absent and reference-based when
    # present; the prompt string differs accordingly.
    src: str = ""
    mt: str
    ref: str | None = None


class ScoreRequest(BaseModel):
    rows: list[Row] = Field(..., min_length=1)


class ScoreResponse(BaseModel):
    model: str
    count: int

    # MetricX is an error metric: lower is better, range roughly 0-25.
    scores: list[float]
    system_score: float


class InfoResponse(BaseModel):
    model: str
    ready: bool
    device: str
    dtype: str | None
    batch_size: int
    max_length: int
    max_rows_per_request: int
    error: str | None = None
