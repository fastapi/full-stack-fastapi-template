from typing import Literal

from pydantic import BaseModel, Field, model_validator


class EmbedRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1)

    # LaBSE ends in a Normalize module, so its output is already unit-length and
    # this is a no-op. Kept explicit so callers don't have to know that.
    normalize: bool = True

    # "float" is readable and fine for small batches. "base64" ships the whole
    # matrix as one float32 blob — roughly 4x smaller and much cheaper to
    # parse once you are pulling tens of thousands of vectors for alignment.
    encoding: Literal["float", "base64"] = "float"


class EmbedResponse(BaseModel):
    model: str
    dim: int
    count: int
    encoding: Literal["float", "base64"]

    # Exactly one of these is populated, per `encoding`.
    vectors: list[list[float]] | None = None
    data: str | None = Field(
        default=None,
        description="base64 of a C-order float32 array with shape (count, dim)",
    )


class SimilarityRequest(BaseModel):
    src: list[str] = Field(..., min_length=1)
    trg: list[str] = Field(..., min_length=1)

    @model_validator(mode="after")
    def _same_length(self) -> "SimilarityRequest":
        if len(self.src) != len(self.trg):
            raise ValueError(
                f"src and trg must be the same length (got {len(self.src)} and {len(self.trg)})"
            )
        return self


class SimilarityResponse(BaseModel):
    model: str
    count: int

    # Full precision. Rounding is a presentation concern and belongs to the
    # caller, not to the model service.
    scores: list[float]
    system_score: float


class InfoResponse(BaseModel):
    model: str
    ready: bool
    device: str
    dim: int | None
    dtype: str | None
    batch_size: int
    max_texts_per_request: int
    error: str | None = None
