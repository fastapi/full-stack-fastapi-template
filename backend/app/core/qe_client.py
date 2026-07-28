"""HTTP client for the CometKiwi deployment of comet-svc.

CometKiwi no longer runs in this process. It shares an image with wmt22-comet-da
(see comet_client) because their dependency trees are identical — only the
checkpoint differs.
"""

from __future__ import annotations

from app.core.config import settings
from app.core.model_service import ModelService

QE = ModelService(
    name="qe-svc",
    base_url=settings.QE_SERVICE_URL,
    connect_timeout=settings.QE_CONNECT_TIMEOUT,
    read_timeout=settings.QE_READ_TIMEOUT,
    chunk_size=2048,
)


async def score(rows: list[dict[str, str]]) -> tuple[list[float], float]:
    """Score src/mt pairs, returning per-pair scores and the corpus mean."""
    return await QE.post_chunked_scores("/v1/score", "rows", rows)
