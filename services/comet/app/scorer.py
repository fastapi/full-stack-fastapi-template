from __future__ import annotations

import asyncio
import logging
import os
import time

import torch
from comet import load_from_checkpoint

from app.config import settings

logger = logging.getLogger(__name__)


class ModelNotReady(RuntimeError):
    """Raised while the checkpoint is still loading, or after a failed load."""


class Scorer:
    """Owns the single resident CometKiwi model."""

    def __init__(self) -> None:
        self._model = None
        self._device = "cpu"
        self._error: str | None = None
        self._sem: asyncio.Semaphore | None = None

    # -- lifecycle ---------------------------------------------------------

    def load(self) -> None:
        """Blocking checkpoint load. Call from a worker thread."""
        name = settings.MODEL_NAME
        path = settings.MODEL_PATH
        if not os.path.exists(path):
            self._error = f"checkpoint not found at {path}"
            logger.error("%s load failed: %s", name, self._error)
            return

        started = time.monotonic()
        try:
            logger.info("Loading %s from %s", name, path)
            model = load_from_checkpoint(path)

            use_cuda = torch.cuda.is_available() and not settings.FORCE_CPU
            if use_cuda:
                model = model.cuda()
            model.eval()

            self._model = model
            self._device = "cuda" if use_cuda else "cpu"
            self._error = None

            if settings.WARMUP:
                self._warmup()

            logger.info(
                "%s ready on %s in %.1fs",
                name,
                self._device,
                time.monotonic() - started,
            )
        except Exception as exc:  # noqa: BLE001 — surfaced via /ready and /v1/info
            self._model = None
            self._error = f"{type(exc).__name__}: {exc}"
            logger.exception("%s load failed", name)

    def _warmup(self) -> None:
        """One tiny forward pass so request #1 isn't the slow one.

        We don't know from the checkpoint alone whether it is reference-free,
        so try {src, mt} and fall back to including a reference.
        """
        row = {"src": "warmup", "mt": "warmup"}
        try:
            self._score_sync([row])
        except Exception:  # noqa: BLE001 — reference-based checkpoint
            self._score_sync([{**row, "ref": "warmup"}])

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
    def error(self) -> str | None:
        return self._error

    def _require(self):
        if self._model is None:
            raise ModelNotReady(self._error or "model is still loading")
        return self._model

    # -- inference ---------------------------------------------------------

    def _score_sync(self, rows: list[dict[str, str]]) -> list[float]:
        """Direct forward pass.

        `model.predict()` spins up its own dataloader and progress bar per call;
        going straight through prepare_sample/forward is materially faster for
        the request-sized batches this service sees.
        """
        model = self._require()

        batch = model.prepare_sample(rows, stage="predict")
        if isinstance(batch, tuple):
            batch = batch[0]
        batch = {k: v.to(model.device) for k, v in batch.items()}

        with torch.no_grad():
            output = model.forward(**batch)

        return [float(s) for s in output.score.tolist()]

    async def score(self, rows: list[dict[str, str]]) -> list[float]:
        self._require()

        if self._sem is None:
            self._sem = asyncio.Semaphore(settings.MAX_CONCURRENT_BATCHES)

        scores: list[float] = []
        async with self._sem:
            # Chunked so peak activation memory tracks BATCH_SIZE, not request
            # size. Each pair is scored independently, so this is numerically
            # identical to one large forward pass.
            for start in range(0, len(rows), settings.BATCH_SIZE):
                chunk = rows[start : start + settings.BATCH_SIZE]
                scores.extend(await asyncio.to_thread(self._score_sync, chunk))

        return scores


scorer = Scorer()
