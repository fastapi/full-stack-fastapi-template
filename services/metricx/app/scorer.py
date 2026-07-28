from __future__ import annotations

import asyncio
import logging
import os
import time

import torch
from transformers import AutoTokenizer

from app.config import settings
from app.metricx_model import MT5ForRegression

logger = logging.getLogger(__name__)


class ModelNotReady(RuntimeError):
    """Raised while the model is still loading, or after a failed load."""


class Scorer:
    """Owns the single resident MetricX model and its tokenizer."""

    def __init__(self) -> None:
        self._model = None
        self._tokenizer = None
        self._device = "cpu"
        self._dtype: str | None = None
        self._error: str | None = None
        self._sem: asyncio.Semaphore | None = None

    # -- lifecycle ---------------------------------------------------------

    def load(self) -> None:
        """Blocking model load. Call from a worker thread."""
        path = settings.MODEL_PATH
        if not os.path.isdir(path):
            self._error = f"model not found at {path}"
            logger.error("MetricX load failed: %s", self._error)
            return

        # The checkpoint may or may not carry its own tokenizer.
        if os.path.exists(os.path.join(path, "spiece.model")) or os.path.exists(
            os.path.join(path, "tokenizer.json")
        ):
            tokenizer_source = path
        else:
            tokenizer_source = settings.TOKENIZER_ID
            logger.info("No tokenizer in %s, falling back to %s", path, tokenizer_source)

        started = time.monotonic()
        try:
            tokenizer = AutoTokenizer.from_pretrained(tokenizer_source)

            use_cuda = torch.cuda.is_available() and not settings.FORCE_CPU
            dtype = torch.bfloat16 if (use_cuda and settings.BF16) else torch.float32

            logger.info("Loading MetricX from %s as %s", path, dtype)
            model = MT5ForRegression.from_pretrained(path, torch_dtype=dtype)
            model.eval()
            if use_cuda:
                model = model.cuda()

            self._model = model
            self._tokenizer = tokenizer
            self._device = "cuda" if use_cuda else "cpu"
            self._dtype = str(dtype).removeprefix("torch.")
            self._error = None

            if settings.WARMUP:
                self._score_sync([{"src": "warmup", "mt": "warmup", "ref": None}])

            logger.info(
                "MetricX ready on %s (%s) in %.1fs",
                self._device,
                self._dtype,
                time.monotonic() - started,
            )
        except Exception as exc:  # noqa: BLE001 — surfaced via /ready and /v1/info
            self._model = None
            self._error = f"{type(exc).__name__}: {exc}"
            logger.exception("MetricX load failed")

    def unload(self) -> None:
        self._model = None
        self._tokenizer = None
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
    def dtype(self) -> str | None:
        return self._dtype

    @property
    def error(self) -> str | None:
        return self._error

    def _require(self):
        if self._model is None:
            raise ModelNotReady(self._error or "model is still loading")
        return self._model, self._tokenizer

    # -- inference ---------------------------------------------------------

    def _score_sync(self, rows: list[dict[str, str | None]]) -> list[float]:
        model, tokenizer = self._require()

        prompts = []
        for row in rows:
            src = row.get("src") or ""
            mt = row["mt"]
            ref = row.get("ref")
            if ref:
                prompts.append(f"source: {src} candidate: {mt} reference: {ref}")
            else:
                prompts.append(f"source: {src} candidate: {mt}")

        # Tokenize without padding first so the EOS token can be dropped safely,
        # matching the MetricX reference predict.py.
        encodings = tokenizer(
            prompts, truncation=True, max_length=settings.MAX_LENGTH, padding=False
        )
        input_ids = [ids[:-1] for ids in encodings["input_ids"]]
        attention_mask = [mask[:-1] for mask in encodings["attention_mask"]]

        batch_size = max(1, settings.BATCH_SIZE)
        scores: list[float] = [0.0] * len(prompts)

        # Length-sorted so each padded batch is only as long as its own longest
        # sequence, not the longest in the whole request.
        order = sorted(range(len(input_ids)), key=lambda i: len(input_ids[i]))

        for start in range(0, len(order), batch_size):
            idx = order[start : start + batch_size]
            batch = tokenizer.pad(
                {
                    "input_ids": [input_ids[i] for i in idx],
                    "attention_mask": [attention_mask[i] for i in idx],
                },
                padding=True,
                return_tensors="pt",
            )
            batch = {k: v.to(model.device) for k, v in batch.items()}

            with torch.no_grad():
                outputs = model(**batch)
                predictions = outputs.predictions.float().cpu().numpy()

            for j, i in enumerate(idx):
                scores[i] = float(predictions[j])

        return scores

    async def score(self, rows: list[dict[str, str | None]]) -> list[float]:
        self._require()

        if self._sem is None:
            self._sem = asyncio.Semaphore(settings.MAX_CONCURRENT_BATCHES)

        async with self._sem:
            return await asyncio.to_thread(self._score_sync, rows)


scorer = Scorer()
