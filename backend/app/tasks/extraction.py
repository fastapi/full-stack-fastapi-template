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
from app.services.ocr import MistralOCRProvider, OCRProviderError
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
    max_retries=3,
    time_limit=600,  # 10 minutes
)  # type: ignore[misc]
def process_ocr_task(self: Any, ingestion_id: str) -> dict[str, Any]:
    """
    Process a PDF ingestion through OCR using Mistral AI.

    Args:
        ingestion_id: UUID of the ingestion record

    Returns:
        dict with OCR results and metadata

    Raises:
        ValueError: If ingestion not found or invalid ID format
        OCRProviderError: If OCR processing fails
        Retry: If task should be retried (transient errors)
    """
    logger.info(f"Starting OCR processing for ingestion: {ingestion_id}")

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
                f"[{ingestion_id}] OCR completed: {ocr_result.total_pages} pages, "
                f"{ocr_result.processing_time_seconds:.2f}s"
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

    except OCRProviderError as e:
        logger.error(f"[{ingestion_id}] OCR provider error: {str(e)}")

        # Update status to FAILED
        with get_db_context() as db:
            ingestion = db.get(Ingestion, ingestion_uuid)
            if ingestion:
                ingestion.status = ExtractionStatus.FAILED
                db.add(ingestion)
                db.commit()

        # Retry on transient errors (rate limits, timeouts)
        if "rate limit" in str(e).lower() or "timeout" in str(e).lower():
            retry_countdown = 2**self.request.retries  # Exponential backoff
            logger.warning(
                f"[{ingestion_id}] Retrying after {retry_countdown}s (attempt {self.request.retries + 1}/3)"
            )
            raise self.retry(exc=e, countdown=retry_countdown, max_retries=3)
        else:
            raise

    except Exception as e:
        logger.error(f"[{ingestion_id}] Unexpected error during OCR: {str(e)}")

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
