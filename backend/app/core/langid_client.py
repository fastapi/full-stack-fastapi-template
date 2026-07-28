"""HTTP client for langid-svc.

Language identification runs in its own container (services/langid), which uses
lingua restricted to English and French. Nothing about it is loaded here.
"""

from __future__ import annotations

from app.core.config import settings
from app.core.model_service import ModelService

LANGID = ModelService(
    name="langid-svc",
    base_url=settings.LANGID_SERVICE_URL,
    connect_timeout=settings.LANGID_CONNECT_TIMEOUT,
    read_timeout=settings.LANGID_READ_TIMEOUT,
    chunk_size=4096,
)


async def detect(texts: list[str]) -> list[tuple[str | None, float]]:
    """Detect the language of each text, in input order.

    Returns (iso_639_1_code_or_None, confidence) per text. None means the
    detector could not decide — an empty string, digits, symbols — not
    "some other language"; see services/langid/app/config.py.
    """
    if not texts:
        return []

    out: list[tuple[str | None, float]] = []
    async with LANGID.client() as client:
        for start in range(0, len(texts), LANGID.chunk_size):
            payload = await LANGID.post(
                client, "/v1/detect", {"texts": texts[start : start + LANGID.chunk_size]}
            )
            out.extend((r["language"], float(r["score"])) for r in payload["results"])

    return out
