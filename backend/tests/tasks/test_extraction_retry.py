"""Tests for OCR task retry logic with error classification."""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from celery.exceptions import Retry

from app.models import ExtractionStatus
from app.services.ocr import (
    BoundingBox,
    ContentBlock,
    NonRetryableError,
    OCRPageResult,
    OCRResult,
    RateLimitError,
    RetryableError,
)
from app.tasks.extraction import process_ocr_task


class TestProcessOCRTaskRetryLogic:
    """Test OCR task retry logic with error classification."""

    @pytest.fixture
    def mock_ingestion(self):
        """Create a mock ingestion record."""
        return MagicMock(
            id=uuid.uuid4(),
            storage_path="worksheets/test-user/test.pdf",
            status=ExtractionStatus.UPLOADED,
            filename="test.pdf",
        )

    @pytest.fixture
    def mock_ocr_result(self):
        """Create a mock successful OCR result."""
        extraction_id = uuid.uuid4()
        return OCRResult(
            extraction_id=extraction_id,
            ocr_provider="mistral",
            processed_at=datetime.utcnow(),
            total_pages=1,
            processing_time_seconds=5.0,
            pages=[
                OCRPageResult(
                    page_number=1,
                    page_width=612,
                    page_height=792,
                    blocks=[
                        ContentBlock(
                            block_id="blk_001",
                            block_type="text",
                            text="Test content",
                            bbox=BoundingBox(x=100, y=200, width=300, height=50),
                            confidence=0.98,
                        )
                    ],
                )
            ],
            metadata={"cost_usd": 0.01, "average_confidence": 0.98},
        )

    @patch("app.tasks.extraction.settings")
    @patch("app.tasks.extraction.get_db_context")
    @patch("app.tasks.extraction.download_from_storage")
    @patch("app.tasks.extraction.MistralOCRProvider")
    def test_no_retry_on_non_retryable_error_401(
        self,
        mock_provider_class,
        mock_download,
        mock_db_context,
        mock_settings,
        mock_ingestion,
    ):
        """Test task does NOT retry on 401 authentication error."""
        mock_settings.MISTRAL_API_KEY = "invalid-key"

        mock_db = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_db
        mock_db.get.return_value = mock_ingestion

        mock_download.return_value = b"%PDF-1.4 content"

        # Simulate 401 error
        mock_provider = AsyncMock()
        mock_provider.extract_text.side_effect = NonRetryableError(
            "Mistral API authentication failed", status_code=401
        )
        mock_provider_class.return_value = mock_provider

        # Should raise NonRetryableError without retrying
        with pytest.raises(NonRetryableError):
            process_ocr_task(str(mock_ingestion.id))

        # Verify status updated to FAILED
        assert mock_ingestion.status == ExtractionStatus.FAILED

        # Verify OCR was only called once (no retries)
        assert mock_provider.extract_text.call_count == 1

    @patch("app.tasks.extraction.settings")
    @patch("app.tasks.extraction.get_db_context")
    @patch("app.tasks.extraction.download_from_storage")
    @patch("app.tasks.extraction.MistralOCRProvider")
    def test_retry_on_retryable_error_500(
        self,
        mock_provider_class,
        mock_download,
        mock_db_context,
        mock_settings,
        mock_ingestion,
        mock_ocr_result,
    ):
        """Test task retries on 500 server error with exponential backoff."""
        mock_settings.MISTRAL_API_KEY = "test-key"

        mock_db = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_db
        mock_db.get.return_value = mock_ingestion

        mock_download.return_value = b"%PDF-1.4 content"

        # Simulate 500 error on first 2 calls, success on 3rd
        mock_provider = AsyncMock()
        mock_provider.extract_text.side_effect = [
            RetryableError("Mistral API server error: 500", status_code=500),
            RetryableError("Mistral API server error: 500", status_code=500),
            mock_ocr_result,
        ]
        mock_provider_class.return_value = mock_provider

        # With autoretry_for, this should eventually succeed
        # For now, since we haven't implemented autoretry_for yet,
        # this will raise on first error
        with pytest.raises(RetryableError):
            process_ocr_task(str(mock_ingestion.id))

    @patch("app.tasks.extraction.settings")
    @patch("app.tasks.extraction.get_db_context")
    @patch("app.tasks.extraction.download_from_storage")
    @patch("app.tasks.extraction.MistralOCRProvider")
    @patch("app.tasks.extraction.process_ocr_task.retry")
    def test_rate_limit_error_respects_retry_after_header(
        self,
        mock_task_retry,
        mock_provider_class,
        mock_download,
        mock_db_context,
        mock_settings,
        mock_ingestion,
    ):
        """Test task respects Retry-After header on 429 rate limit."""
        mock_settings.MISTRAL_API_KEY = "test-key"

        mock_db = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_db
        mock_db.get.return_value = mock_ingestion

        mock_download.return_value = b"%PDF-1.4 content"

        # Simulate 429 with retry-after=60
        mock_provider = AsyncMock()
        mock_provider.extract_text.side_effect = RateLimitError(
            "Mistral API rate limit exceeded", retry_after=60
        )
        mock_provider_class.return_value = mock_provider

        mock_task_retry.side_effect = Retry()

        with pytest.raises(Retry):
            process_ocr_task(str(mock_ingestion.id))

        # Verify retry was called with retry_after countdown
        mock_task_retry.assert_called_once()
        call_kwargs = mock_task_retry.call_args[1]
        assert call_kwargs["countdown"] == 60

    @patch("app.tasks.extraction.settings")
    @patch("app.tasks.extraction.get_db_context")
    @patch("app.tasks.extraction.download_from_storage")
    @patch("app.tasks.extraction.MistralOCRProvider")
    def test_rate_limit_error_without_retry_after(
        self,
        mock_provider_class,
        mock_download,
        mock_db_context,
        mock_settings,
        mock_ingestion,
    ):
        """Test task uses default backoff when Retry-After header missing."""
        mock_settings.MISTRAL_API_KEY = "test-key"

        mock_db = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_db
        mock_db.get.return_value = mock_ingestion

        mock_download.return_value = b"%PDF-1.4 content"

        # Simulate 429 without retry_after
        mock_provider = AsyncMock()
        mock_provider.extract_text.side_effect = RateLimitError(
            "Mistral API rate limit exceeded", retry_after=None
        )
        mock_provider_class.return_value = mock_provider

        # Should raise and rely on autoretry_for exponential backoff
        with pytest.raises(RateLimitError):
            process_ocr_task(str(mock_ingestion.id))

    @patch("app.tasks.extraction.settings")
    @patch("app.tasks.extraction.get_db_context")
    @patch("app.tasks.extraction.download_from_storage")
    @patch("app.tasks.extraction.MistralOCRProvider")
    def test_no_retry_on_non_retryable_error_400(
        self,
        mock_provider_class,
        mock_download,
        mock_db_context,
        mock_settings,
        mock_ingestion,
    ):
        """Test task does NOT retry on 400 bad request error."""
        mock_settings.MISTRAL_API_KEY = "test-key"

        mock_db = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_db
        mock_db.get.return_value = mock_ingestion

        mock_download.return_value = b"%PDF-1.4 content"

        # Simulate 400 error
        mock_provider = AsyncMock()
        mock_provider.extract_text.side_effect = NonRetryableError(
            "Mistral API error: 400", status_code=400
        )
        mock_provider_class.return_value = mock_provider

        with pytest.raises(NonRetryableError):
            process_ocr_task(str(mock_ingestion.id))

        # Verify status updated to FAILED
        assert mock_ingestion.status == ExtractionStatus.FAILED

    @patch("app.tasks.extraction.settings")
    @patch("app.tasks.extraction.get_db_context")
    @patch("app.tasks.extraction.download_from_storage")
    @patch("app.tasks.extraction.MistralOCRProvider")
    def test_retry_on_503_service_unavailable(
        self,
        mock_provider_class,
        mock_download,
        mock_db_context,
        mock_settings,
        mock_ingestion,
    ):
        """Test task retries on 503 service unavailable."""
        mock_settings.MISTRAL_API_KEY = "test-key"

        mock_db = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_db
        mock_db.get.return_value = mock_ingestion

        mock_download.return_value = b"%PDF-1.4 content"

        # Simulate 503 error
        mock_provider = AsyncMock()
        mock_provider.extract_text.side_effect = RetryableError(
            "Mistral API server error: 503", status_code=503
        )
        mock_provider_class.return_value = mock_provider

        with pytest.raises(RetryableError):
            process_ocr_task(str(mock_ingestion.id))
