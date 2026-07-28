"""HTTP client for metricx-svc.

MetricX has its own container because MT5ForRegression subclasses transformers
internals, so it needs to track transformers independently of comet.
"""

from __future__ import annotations

from app.core.config import settings
from app.core.model_service import ModelService

METRICX = ModelService(
    name="metricx-svc",
    base_url=settings.METRICX_SERVICE_URL,
    connect_timeout=settings.METRICX_CONNECT_TIMEOUT,
    read_timeout=settings.METRICX_READ_TIMEOUT,
    # MetricX sequences are long (up to MAX_LENGTH tokens), so keep the
    # per-request payload well under the service's own cap.
    chunk_size=1024,
)


async def score(rows: list[dict[str, str | None]]) -> tuple[list[float], float]:
    """Score src/mt/ref rows. ref may be None for reference-free scoring."""
    return await METRICX.post_chunked_scores("/v1/score", "rows", rows)
