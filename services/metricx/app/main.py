from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.schemas import InfoResponse, ScoreRequest, ScoreResponse
from app.scorer import ModelNotReady, scorer

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

MODEL_NAME = "metricx"


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(asyncio.to_thread(scorer.load))
    try:
        yield
    finally:
        task.cancel()
        scorer.unload()


app = FastAPI(
    title="MetricX scoring service",
    version="0.1.0",
    summary="MetricX-24 hybrid regression. src/mt/ref in, error scores out.",
    lifespan=lifespan,
)


@app.exception_handler(ModelNotReady)
async def _model_not_ready(request: Request, exc: ModelNotReady) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": str(exc)},
        headers={"Retry-After": "10"},
    )


@app.get("/health", summary="Liveness — is the process up")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", summary="Readiness — are the weights resident")
async def ready(response: Response) -> dict[str, object]:
    if not scorer.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"ready": False, "error": scorer.error}
    return {"ready": True, "device": scorer.device}


@app.get("/v1/info", response_model=InfoResponse)
async def info() -> InfoResponse:
    return InfoResponse(
        model=MODEL_NAME,
        ready=scorer.ready,
        device=scorer.device,
        dtype=scorer.dtype,
        batch_size=settings.BATCH_SIZE,
        max_length=settings.MAX_LENGTH,
        max_rows_per_request=settings.MAX_ROWS_PER_REQUEST,
        error=scorer.error,
    )


@app.post("/v1/score", response_model=ScoreResponse)
async def score(req: ScoreRequest) -> ScoreResponse:
    if len(req.rows) > settings.MAX_ROWS_PER_REQUEST:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"{len(req.rows)} rows exceeds MAX_ROWS_PER_REQUEST="
                f"{settings.MAX_ROWS_PER_REQUEST}; chunk the request"
            ),
        )

    rows = [{"src": r.src, "mt": r.mt, "ref": r.ref} for r in req.rows]
    scores = await scorer.score(rows)

    return ScoreResponse(
        model=MODEL_NAME,
        count=len(scores),
        scores=scores,
        system_score=sum(scores) / len(scores) if scores else 0.0,
    )
