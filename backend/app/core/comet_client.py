"""HTTP client for the wmt22-comet-da deployment of comet-svc.

Same image as qe-svc, different checkpoint and therefore a different URL.
Reference-based, so every row carries a ref.
"""

from __future__ import annotations

from app.core.config import settings
from app.core.model_service import ModelService

COMET = ModelService(
    name="comet-svc",
    base_url=settings.COMET_SERVICE_URL,
    connect_timeout=settings.COMET_CONNECT_TIMEOUT,
    read_timeout=settings.COMET_READ_TIMEOUT,
    chunk_size=2048,
)


async def score(rows: list[dict[str, str]]) -> tuple[list[float], float]:
    """Score src/mt/ref triples, returning per-row scores and the corpus mean."""
    return await COMET.post_chunked_scores("/v1/score", "rows", rows)
