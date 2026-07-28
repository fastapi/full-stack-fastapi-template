from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.detector import ModelNotReady, detector
from app.schemas import Detection, DetectRequest, DetectResponse, InfoResponse

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

MODEL_NAME = "lingua"


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(asyncio.to_thread(detector.load))
    try:
        yield
    finally:
        task.cancel()
        detector.unload()


app = FastAPI(
    title="Language identification service (lingua)",
    version="0.1.0",
    summary="Text in, ISO 639-1 codes out. Restricted to English and French.",
    lifespan=lifespan,
)


@app.exception_handler(ModelNotReady)
async def _model_not_ready(request: Request, exc: ModelNotReady) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": str(exc)},
        headers={"Retry-After": "5"},
    )


@app.get("/health", summary="Liveness — is the process up")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", summary="Readiness — are the n-gram models loaded")
async def ready(response: Response) -> dict[str, object]:
    if not detector.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"ready": False, "error": detector.error}
    return {"ready": True, "languages": detector.codes}


@app.get("/v1/info", response_model=InfoResponse)
async def info() -> InfoResponse:
    return InfoResponse(
        model=MODEL_NAME,
        ready=detector.ready,
        languages=detector.codes,
        low_accuracy_mode=settings.LOW_ACCURACY_MODE,
        min_confidence=settings.MIN_CONFIDENCE,
        max_texts_per_request=settings.MAX_TEXTS_PER_REQUEST,
        error=detector.error,
    )


@app.post("/v1/detect", response_model=DetectResponse)
async def detect(req: DetectRequest) -> DetectResponse:
    if len(req.texts) > settings.MAX_TEXTS_PER_REQUEST:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"{len(req.texts)} texts exceeds MAX_TEXTS_PER_REQUEST="
                f"{settings.MAX_TEXTS_PER_REQUEST}; chunk the request"
            ),
        )

    pairs = await detector.detect(req.texts)

    return DetectResponse(
        model=MODEL_NAME,
        count=len(pairs),
        languages=detector.codes,
        results=[Detection(language=lang, score=score) for lang, score in pairs],
    )
