from __future__ import annotations

import asyncio
import logging
import os
import time

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from app.config import settings

logger = logging.getLogger(__name__)


class ModelNotReady(RuntimeError):
    """Raised while the model is still loading, or after a failed load."""


class Encoder:
    """Owns the single resident LaBSE model.

    Two things matter for throughput here and neither is parallelism:

    1. Hand sentence-transformers the whole list in one `encode` call. It sorts
       by length internally before batching, so padding waste disappears for
       free — but only if the caller doesn't loop.
    2. Encode each distinct string once. Translation memories repeat heavily.
    """

    def __init__(self) -> None:
        self._model: SentenceTransformer | None = None
        self._device = "cpu"
        self._dim: int | None = None
        self._dtype: str | None = None
        self._error: str | None = None
        self._sem: asyncio.Semaphore | None = None

    # -- lifecycle ---------------------------------------------------------

    def load(self) -> None:
        """Blocking model load. Call from a worker thread, not the event loop."""
        path = settings.MODEL_PATH
        if not os.path.isdir(path):
            self._error = f"model not found at {path}"
            logger.error("LaBSE load failed: %s", self._error)
            return

        started = time.monotonic()
        try:
            use_cuda = torch.cuda.is_available() and not settings.FORCE_CPU
            device = "cuda" if use_cuda else "cpu"
            logger.info("Loading LaBSE from %s onto %s", path, device)

            model = SentenceTransformer(path, device=device)
            if use_cuda and settings.FP16:
                model = model.half()
            model.eval()

            self._model = model
            self._device = device
            # Renamed in sentence-transformers 5.x; accept either so pinning the
            # lock to an older version later doesn't break the load.
            get_dim = getattr(
                model, "get_embedding_dimension", None
            ) or model.get_sentence_embedding_dimension
            self._dim = get_dim()
            self._dtype = str(next(model.parameters()).dtype).removeprefix("torch.")
            self._error = None

            if settings.WARMUP:
                self._encode_sync(["warmup"], normalize=True)

            logger.info(
                "LaBSE ready on %s (%s, dim=%d) in %.1fs",
                device,
                self._dtype,
                self._dim,
                time.monotonic() - started,
            )
        except Exception as exc:  # noqa: BLE001 — surfaced via /ready and /v1/info
            self._model = None
            self._error = f"{type(exc).__name__}: {exc}"
            logger.exception("LaBSE load failed")

    def unload(self) -> None:
        self._model = None
        if self._device == "cuda":
            torch.cuda.empty_cache()

    # -- state -------------------------------------------------------------

    @property
    def ready(self) -> bool:
        return self._model is not None

    @property
    def device(self) -> str:
        return self._device

    @property
    def dim(self) -> int | None:
        return self._dim

    @property
    def dtype(self) -> str | None:
        return self._dtype

    @property
    def error(self) -> str | None:
        return self._error

    def _require(self) -> SentenceTransformer:
        if self._model is None:
            raise ModelNotReady(self._error or "model is still loading")
        return self._model

    # -- inference ---------------------------------------------------------

    def _encode_sync(self, texts: list[str], normalize: bool) -> np.ndarray:
        model = self._require()
        with torch.inference_mode():
            vectors = model.encode(
                texts,
                batch_size=settings.BATCH_SIZE,
                convert_to_numpy=True,
                normalize_embeddings=normalize,
                show_progress_bar=False,
            )
        # fp16 weights produce fp16 output; callers want a stable wire format.
        return np.ascontiguousarray(vectors, dtype=np.float32)

    async def encode(self, texts: list[str], normalize: bool = True) -> np.ndarray:
        """Encode `texts`, deduplicating first and restoring the input order."""
        self._require()

        # Insertion-ordered mapping from text -> index into the unique batch.
        positions: dict[str, int] = {}
        order: list[int] = []
        for text in texts:
            order.append(positions.setdefault(text, len(positions)))

        unique = list(positions)
        if len(unique) < len(texts):
            logger.debug("deduplicated %d texts to %d", len(texts), len(unique))

        if self._sem is None:
            self._sem = asyncio.Semaphore(settings.MAX_CONCURRENT_BATCHES)

        async with self._sem:
            vectors = await asyncio.to_thread(self._encode_sync, unique, normalize)

        return vectors[order]


encoder = Encoder()
