"""Extraction pipeline tasks for processing PDFs and worksheets."""

import asyncio
import logging
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine
from app.models import ExtractionStatus, Ingestion
from app.services.ocr import (
    MistralOCRProvider,
    NonRetryableError,
    OCRProviderError,
    RateLimitError,
    RetryableError,
)
from app.services.storage import download_from_storage
from app.worker import celery_app

logger = logging.getLogger(__name__)


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Database session context manager for Celery tasks."""
    with Session(engine) as session:
        yield session


@celery_app.task(
    bind=True,
    name="app.tasks.extraction.process_ocr",
    autoretry_for=(RetryableError,),  # Auto-retry on transient errors
    retry_backoff=True,  # Exponential backoff: 1s, 2s, 4s, 8s...
    retry_backoff_max=600,  # Cap backoff at 10 minutes
    retry_jitter=True,  # Add randomness to prevent thundering herd
    retry_kwargs={"max_retries": 3},
    time_limit=600,  # 10 minutes max per attempt
)  # type: ignore[misc]
def process_ocr_task(self: Any, ingestion_id: str) -> dict[str, Any]:
    """
    Process a PDF ingestion through OCR using Mistral AI.

    Automatically retries on RetryableError (500, 502, 503, 504, 408) with
    exponential backoff. Does NOT retry on NonRetryableError (400, 401, 403, 404).
    Special handling for RateLimitError (429) to respect Retry-After header.

    Args:
        ingestion_id: UUID of the ingestion record

    Returns:
        dict with OCR results and metadata

    Raises:
        ValueError: If ingestion not found or invalid ID format
        NonRetryableError: Permanent errors (auth, bad request)
        RetryableError: Transient errors (after max retries exhausted)
        RateLimitError: Rate limit errors (after max retries exhausted)
    """
    logger.info(
        f"Starting OCR for {ingestion_id} (attempt {self.request.retries + 1})"
    )

    # Validate ingestion_id format
    try:
        ingestion_uuid = uuid.UUID(ingestion_id)
    except ValueError as e:
        logger.error(f"Invalid ingestion ID format: {ingestion_id}")
        raise ValueError(f"Invalid ingestion ID format: {ingestion_id}") from e

    try:
        # Fetch ingestion record
        with get_db_context() as db:
            ingestion = db.get(Ingestion, ingestion_uuid)
            if not ingestion:
                logger.error(f"Ingestion {ingestion_id} not found in database")
                raise ValueError(f"Ingestion {ingestion_id} not found")

            # Update status to OCR_PROCESSING
            ingestion.status = ExtractionStatus.OCR_PROCESSING
            db.add(ingestion)
            db.commit()
            logger.info(f"[{ingestion_id}] Status updated to OCR_PROCESSING")

            # Download PDF from storage
            logger.info(
                f"[{ingestion_id}] Downloading PDF from storage: {ingestion.storage_path}"
            )
            pdf_bytes = download_from_storage(ingestion.storage_path)
            logger.info(
                f"[{ingestion_id}] Downloaded {len(pdf_bytes)} bytes from storage"
            )

            # Run OCR extraction
            logger.info(f"[{ingestion_id}] Starting Mistral OCR extraction")
            if not settings.MISTRAL_API_KEY:
                raise ValueError("MISTRAL_API_KEY not configured. Cannot process OCR.")

            provider = MistralOCRProvider(api_key=settings.MISTRAL_API_KEY)

            # Run async OCR extraction in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                ocr_result = loop.run_until_complete(provider.extract_text(pdf_bytes))
            finally:
                loop.close()

            logger.info(
                f"[{ingestion_id}] OCR completed successfully",
                extra={
                    "ingestion_id": ingestion_id,
                    "provider": ocr_result.ocr_provider,
                    "total_pages": ocr_result.total_pages,
                    "processing_time_seconds": ocr_result.processing_time_seconds,
                    "retry_count": self.request.retries,
                },
            )

            # Update ingestion status to OCR_COMPLETE
            ingestion.status = ExtractionStatus.OCR_COMPLETE
            db.add(ingestion)
            db.commit()
            logger.info(f"[{ingestion_id}] Status updated to OCR_COMPLETE")

            return {
                "status": "completed",
                "ingestion_id": ingestion_id,
                "task_id": self.request.id,
                "total_pages": ocr_result.total_pages,
                "processing_time_seconds": ocr_result.processing_time_seconds,
                "ocr_provider": ocr_result.ocr_provider,
                "metadata": ocr_result.metadata,
            }

    except RateLimitError as e:
        # Special handling for 429 - respect Retry-After header
        logger.warning(
            f"[{ingestion_id}] Rate limited (429). "
            f"Retry-After: {e.retry_after}s. Attempt {self.request.retries + 1}/3",
            extra={
                "ingestion_id": ingestion_id,
                "error_type": "RateLimitError",
                "status_code": 429,
                "retry_after": e.retry_after,
                "retry_count": self.request.retries,
            },
        )

        if e.retry_after:
            # Override default backoff with Retry-After value from API
            raise self.retry(exc=e, countdown=e.retry_after)
        else:
            # Let autoretry_for handle it with exponential backoff
            raise

    except NonRetryableError as e:
        # Don't retry - permanent errors (401, 400, 403, 404)
        logger.error(
            f"[{ingestion_id}] Non-retryable error: {e}",
            extra={
                "ingestion_id": ingestion_id,
                "error_type": type(e).__name__,
                "status_code": e.status_code,
            },
        )

        # Update status to FAILED
        with get_db_context() as db:
            ingestion = db.get(Ingestion, ingestion_uuid)
            if ingestion:
                ingestion.status = ExtractionStatus.FAILED
                db.add(ingestion)
                db.commit()

        raise  # Don't retry, fail immediately

    except RetryableError as e:
        # Transient errors - will be caught by autoretry_for
        logger.warning(
            f"[{ingestion_id}] Retryable error: {e}. "
            f"Attempt {self.request.retries + 1}/3",
            extra={
                "ingestion_id": ingestion_id,
                "error_type": type(e).__name__,
                "status_code": e.status_code,
                "retry_count": self.request.retries,
            },
        )
        raise  # Let autoretry_for handle it with exponential backoff

    except Exception as e:
        # Unexpected error - log and fail
        logger.error(
            f"[{ingestion_id}] Unexpected error: {str(e)}",
            exc_info=True,
            extra={
                "ingestion_id": ingestion_id,
                "error_type": type(e).__name__,
            },
        )

        # Update status to FAILED
        try:
            with get_db_context() as db:
                ingestion = db.get(Ingestion, ingestion_uuid)
                if ingestion:
                    ingestion.status = ExtractionStatus.FAILED
                    db.add(ingestion)
                    db.commit()
        except Exception as db_error:
            logger.error(
                f"[{ingestion_id}] Failed to update status to FAILED: {str(db_error)}"
            )

        raise


@celery_app.task(bind=True, name="app.tasks.extraction.process_pdf")  # type: ignore[misc]
def process_pdf_task(self: Any, extraction_id: str) -> dict[str, Any]:
    """
    Process a PDF worksheet through the extraction pipeline.

    Pipeline stages:
    1. Fetch PDF from Supabase Storage
    2. OCR - Extract text and layout
    3. Segmentation - Identify question boundaries
    4. Tagging - Apply curriculum tags
    5. Store results in database

    Args:
        extraction_id: UUID of the extraction record

    Returns:
        dict with extraction results and metadata
    """
    logger.info(f"Starting PDF extraction for: {extraction_id}")

    try:
        # Stage 1: Fetch PDF (to be implemented)
        logger.info(f"[{extraction_id}] Stage 1: Fetching PDF from storage")
        # TODO: Implement Supabase Storage fetch

        # Stage 2: OCR (to be implemented)
        logger.info(f"[{extraction_id}] Stage 2: Running OCR")
        # TODO: Implement PaddleOCR integration

        # Stage 3: Segmentation (to be implemented)
        logger.info(f"[{extraction_id}] Stage 3: Segmenting questions")
        # TODO: Implement question boundary detection

        # Stage 4: Tagging (to be implemented)
        logger.info(f"[{extraction_id}] Stage 4: Applying curriculum tags")
        # TODO: Implement ML tagging

        # Stage 5: Store results (to be implemented)
        logger.info(f"[{extraction_id}] Stage 5: Storing results")
        # TODO: Implement database persistence

        logger.info(f"Extraction completed successfully: {extraction_id}")

        return {
            "status": "completed",
            "extraction_id": extraction_id,
            "task_id": self.request.id,
            "questions_extracted": 0,  # Placeholder
            "message": "PDF extraction completed (placeholder - implementation pending)",
        }

    except Exception as e:
        logger.error(f"Extraction failed for {extraction_id}: {str(e)}")
        # Update extraction status to FAILED in database
        raise
