"""HTTP client for labse-svc.

LaBSE no longer runs in this process. Encoding happens in a purpose-built
container (services/labse); alignment, faiss and TMX stay here because they are
business logic, not a model primitive.
"""

from __future__ import annotations

import base64

import numpy as np

from app.core.config import settings
from app.core.model_service import ModelService

# LaBSE is fixed at 768 dimensions; used only to shape an empty result.
DIM = 768

LABSE = ModelService(
    name="labse-svc",
    base_url=settings.LABSE_SERVICE_URL,
    connect_timeout=settings.LABSE_CONNECT_TIMEOUT,
    read_timeout=settings.LABSE_READ_TIMEOUT,
    chunk_size=4096,
)


async def embed(texts: list[str], normalize: bool = True) -> np.ndarray:
    """Encode `texts`, returning a (len(texts), 768) float32 array."""
    if not texts:
        return np.zeros((0, DIM), dtype=np.float32)

    chunks: list[np.ndarray] = []
    async with LABSE.client() as client:
        for start in range(0, len(texts), LABSE.chunk_size):
            payload = await LABSE.post(
                client,
                "/v1/embed",
                {
                    "texts": texts[start : start + LABSE.chunk_size],
                    "normalize": normalize,
                    # base64 ships the matrix as one float32 blob — roughly 4x
                    # smaller than JSON floats and far cheaper to parse.
                    "encoding": "base64",
                },
            )
            vectors = np.frombuffer(
                base64.b64decode(payload["data"]), dtype=np.float32
            ).reshape(payload["count"], payload["dim"])
            chunks.append(vectors)

    # frombuffer returns a read-only view; copy so callers can normalise in place.
    return np.ascontiguousarray(np.vstack(chunks))


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
