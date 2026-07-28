"""HTTP client for labse-svc.

LaBSE no longer runs in this process. Encoding, pairwise similarity and the
alignment kNN all happen in a purpose-built container (services/labse). What
stays here is business logic: the length filter, language routing, TMX.

No embedding crosses this boundary any more. `/v1/embed` still exists on the
service for other consumers, but nothing in this app calls it — alignment used
to pull ~4 KB per sentence over HTTP only to feed a local faiss index, and now
sends text and receives index pairs.
"""

from __future__ import annotations

from app.core.config import settings
from app.core.model_service import ModelService

LABSE = ModelService(
    name="labse-svc",
    base_url=settings.LABSE_SERVICE_URL,
    connect_timeout=settings.LABSE_CONNECT_TIMEOUT,
    read_timeout=settings.LABSE_READ_TIMEOUT,
    chunk_size=4096,
)


async def align(
    src: list[str],
    trg: list[str],
    k: int = 4,
    min_score: float = 1.1,
) -> list[tuple[int, int, float]]:
    """Align two sentence lists, returning (src_idx, trg_idx, score) triples.

    Not chunked, unlike the other calls here: kNN is global over the corpus, so
    splitting the request would score each part against a partial index and
    return different pairs. The service caps the size instead.
    """
    if not src or not trg:
        return []

    async with LABSE.client() as client:
        payload = await LABSE.post(
            client,
            "/v1/align",
            {"src": src, "trg": trg, "k": k, "min_score": min_score},
        )

    return [(p["src_idx"], p["trg_idx"], p["score"]) for p in payload["pairs"]]


async def similarity(src: list[str], trg: list[str]) -> tuple[list[float], float]:
    """Row-wise cosine for paired sentences, plus the corpus mean.

    Computed service-side so only N scores cross the wire instead of 2N vectors.
    """
    if len(src) != len(trg):
        raise ValueError(
            f"src and trg must be the same length (got {len(src)} and {len(trg)})"
        )
    if not src:
        return [], 0.0

    # The service counts src + trg against its request cap, so pairs chunk at
    # half the text budget.
    pairs_per_chunk = LABSE.chunk_size // 2

    scores: list[float] = []
    async with LABSE.client() as client:
        for start in range(0, len(src), pairs_per_chunk):
            stop = start + pairs_per_chunk
            payload = await LABSE.post(
                client,
                "/v1/similarity",
                {"src": src[start:stop], "trg": trg[start:stop]},
            )
            scores.extend(payload["scores"])

    # Recomputed over all scores — a mean of per-chunk means would be wrong
    # whenever the last chunk is short.
    return scores, sum(scores) / len(scores)
