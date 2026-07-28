from pydantic import BaseModel, Field


class DetectRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1)


class Detection(BaseModel):
    # ISO 639-1, or None when the detector cannot decide (empty strings,
    # numbers, symbols). Note this does NOT mean "some other language" — see
    # the LANGUAGES note in config.py.
    language: str | None
    score: float


class DetectResponse(BaseModel):
    model: str
    count: int
    languages: list[str]
    results: list[Detection]


class InfoResponse(BaseModel):
    model: str
    ready: bool
    languages: list[str]
    low_accuracy_mode: bool
    min_confidence: float
    max_texts_per_request: int
    error: str | None = None
