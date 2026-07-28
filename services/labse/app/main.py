from __future__ import annotations

import asyncio
import base64
import logging
import os
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.encoder import ModelNotReady, encoder
from app.schemas import (
    EmbedRequest,
    EmbedResponse,
    InfoResponse,
    SimilarityRequest,
    SimilarityResponse,
)

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("labse")

MODEL_NAME = "labse"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load off the event loop and do not await it: the process starts serving
    # immediately so /health answers during a cold start, and /ready gates the
    # traffic until the weights are actually resident.
    task = asyncio.create_task(asyncio.to_thread(encoder.load))
    try:
        yield
    finally:
        task.cancel()
        encoder.unload()


app = FastAPI(
    title="LaBSE embedding service",
    version="0.1.0",
    summary="Vectors in, vectors out. No alignment, no persistence, no auth.",
    lifespan=lifespan,
)


@app.exception_handler(ModelNotReady)
async def _model_not_ready(request: Request, exc: ModelNotReady) -> JSONResponse:
    # 503 + Retry-After is the contract that lets a batch worker treat a cold
    # start as "come back later" instead of a failure.
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
    if not encoder.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"ready": False, "error": encoder.error}
    return {"ready": True, "device": encoder.device}


@app.get("/v1/info", response_model=InfoResponse)
async def info() -> InfoResponse:
    return InfoResponse(
        model=MODEL_NAME,
        ready=encoder.ready,
        device=encoder.device,
        dim=encoder.dim,
        dtype=encoder.dtype,
        batch_size=settings.BATCH_SIZE,
        max_texts_per_request=settings.MAX_TEXTS_PER_REQUEST,
        error=encoder.error,
    )


def _check_size(n: int) -> None:
    if n > settings.MAX_TEXTS_PER_REQUEST:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"{n} texts exceeds MAX_TEXTS_PER_REQUEST="
                f"{settings.MAX_TEXTS_PER_REQUEST}; chunk the request"
            ),
        )


@app.post("/v1/embed", response_model=EmbedResponse)
async def embed(req: EmbedRequest) -> EmbedResponse:
    _check_size(len(req.texts))

    vectors = await encoder.encode(req.texts, normalize=req.normalize)
    count, dim = vectors.shape

    if req.encoding == "base64":
        return EmbedResponse(
            model=MODEL_NAME,
            dim=dim,
            count=count,
            encoding="base64",
            data=base64.b64encode(vectors.tobytes()).decode("ascii"),
        )

    return EmbedResponse(
        model=MODEL_NAME,
        dim=dim,
        count=count,
        encoding="float",
        vectors=vectors.tolist(),
    )


@app.post("/v1/similarity", response_model=SimilarityResponse)
async def similarity(req: SimilarityRequest) -> SimilarityResponse:
    _check_size(len(req.src) + len(req.trg))

    src = [s.strip() for s in req.src]
    trg = [s.strip() for s in req.trg]

    # One encode call over both sides: more work per forward pass, and the
    # dedup in Encoder.encode catches strings shared between src and trg.
    vectors = await encoder.encode(src + trg, normalize=True)
    src_vecs, trg_vecs = vectors[: len(src)], vectors[len(src) :]

    # Row-wise cosine — only the diagonal of the full matmul is ever used, so
    # never materialise the n x n product.
    scores = np.einsum("ij,ij->i", src_vecs, trg_vecs)

    return SimilarityResponse(
        model=MODEL_NAME,
        count=len(scores),
        scores=[float(s) for s in scores],
        system_score=float(scores.mean()) if len(scores) else 0.0,
    )
