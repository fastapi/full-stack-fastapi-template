from __future__ import annotations

import asyncio
import logging
import time

from lingua import IsoCode639_1, LanguageDetectorBuilder

from app.config import settings

logger = logging.getLogger(__name__)


class ModelNotReady(RuntimeError):
    """Raised while the n-gram models are still loading, or after a failure."""


class Detector:
    """Owns the single resident lingua detector.

    Unlike the other model services there is nothing to mount: lingua ships its
    n-gram data inside the wheel, so this container has no /data dependency.
    """

    def __init__(self) -> None:
        self._detector = None
        self._codes: list[str] = []
        self._error: str | None = None

    # -- lifecycle ---------------------------------------------------------

    def load(self) -> None:
        """Blocking build of the detector. Call from a worker thread."""
        started = time.monotonic()
        try:
            codes = settings.language_codes
            if len(codes) < 2:
                raise ValueError(f"need at least two languages, got {codes!r}")

            iso = [getattr(IsoCode639_1, c.upper()) for c in codes]
            builder = LanguageDetectorBuilder.from_iso_codes_639_1(*iso)

            if settings.LOW_ACCURACY_MODE:
                builder = builder.with_low_accuracy_mode()
            if settings.PRELOAD:
                # Otherwise the first request pays for loading the n-gram
                # models and /ready would be lying.
                builder = builder.with_preloaded_language_models()

            self._detector = builder.build()
            self._codes = codes
            self._error = None

            logger.info(
                "lingua ready for %s in %.1fs (low_accuracy=%s)",
                ",".join(codes),
                time.monotonic() - started,
                settings.LOW_ACCURACY_MODE,
            )
        except Exception as exc:  # noqa: BLE001 — surfaced via /ready and /v1/info
            self._detector = None
            self._error = f"{type(exc).__name__}: {exc}"
            logger.exception("lingua build failed")

    def unload(self) -> None:
        if self._detector is not None:
            self._detector.unload_language_models()
        self._detector = None

    # -- state -------------------------------------------------------------

    @property
    def ready(self) -> bool:
        return self._detector is not None

    @property
    def codes(self) -> list[str]:
        return self._codes or settings.language_codes

    @property
    def error(self) -> str | None:
        return self._error

    def _require(self):
        if self._detector is None:
            raise ModelNotReady(self._error or "detector is still loading")
        return self._detector

    # -- inference ---------------------------------------------------------

    def _detect_sync(self, texts: list[str]) -> list[tuple[str | None, float]]:
        detector = self._require()

        # Two passes, both parallelised in Rust:
        #   detect_*  applies lingua's minimum-relative-distance rule and
        #             returns None when it genuinely cannot decide
        #   confidence gives the score the API contract promises
        languages = detector.detect_languages_in_parallel_of(texts)
        confidences = detector.compute_language_confidence_values_in_parallel(texts)

        results: list[tuple[str | None, float]] = []
        for language, values in zip(languages, confidences):
            if language is None:
                results.append((None, 0.0))
                continue

            code = language.iso_code_639_1.name.lower()
            score = next((v.value for v in values if v.language == language), 0.0)

            if score < settings.MIN_CONFIDENCE:
                results.append((None, float(score)))
            else:
                results.append((code, float(score)))

        return results

    async def detect(self, texts: list[str]) -> list[tuple[str | None, float]]:
        self._require()
        # Rust-side work; keep it off the event loop.
        return await asyncio.to_thread(self._detect_sync, texts)


detector = Detector()
