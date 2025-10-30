"""Tests for extraction pipeline Celery tasks."""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from celery.exceptions import Retry

from app.models import ExtractionStatus
from app.services.ocr import (
    BoundingBox,
    ContentBlock,
    OCRPageResult,
    OCRProviderError,
    OCRResult,
)
from app.tasks.extraction import process_ocr_task


class TestProcessOCRTask:
    """Test OCR processing Celery task."""

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
        """Create a mock OCR result."""
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
                            text="Question 1: Solve for x",
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
    def test_process_ocr_task_success(
        self,
        mock_provider_class,
        mock_download,
        mock_db_context,
        mock_settings,
        mock_ingestion,
        mock_ocr_result,
    ):
        """Test successful OCR processing."""
        # Setup mocks
        mock_settings.MISTRAL_API_KEY = "test-api-key"

        mock_db = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_db
        mock_db.get.return_value = mock_ingestion

        mock_download.return_value = b"%PDF-1.4 fake content"

        mock_provider = AsyncMock()
        mock_provider.extract_text.return_value = mock_ocr_result
        mock_provider_class.return_value = mock_provider

        # Execute task
        result = process_ocr_task(str(mock_ingestion.id))

        # Verify result
        assert result["status"] == "completed"
        assert result["ingestion_id"] == str(mock_ingestion.id)
        assert result["total_pages"] == 1
        assert result["processing_time_seconds"] == 5.0

        # Verify database calls
        from app.models import Ingestion

        mock_db.get.assert_called_once_with(Ingestion, mock_ingestion.id)
        assert mock_db.commit.call_count == 2  # Status OCR_PROCESSING + OCR_COMPLETE

        # Verify ingestion status was updated to OCR_COMPLETE
        assert mock_ingestion.status == ExtractionStatus.OCR_COMPLETE

        # Verify storage download
        mock_download.assert_called_once_with(mock_ingestion.storage_path)

        # Verify OCR provider was called
        mock_provider.extract_text.assert_called_once()

    @patch("app.tasks.extraction.get_db_context")
    def test_process_ocr_task_ingestion_not_found(self, mock_db_context):
        """Test task fails when ingestion record not found."""
        mock_db = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_db
        mock_db.get.return_value = None

        ingestion_id = str(uuid.uuid4())

        with pytest.raises(ValueError, match="Ingestion .* not found"):
            process_ocr_task(ingestion_id)

    @patch("app.tasks.extraction.get_db_context")
    @patch("app.tasks.extraction.download_from_storage")
    @patch("app.tasks.extraction.MistralOCRProvider")
    def test_process_ocr_task_storage_error(
        self, mock_provider_class, mock_download, mock_db_context, mock_ingestion
    ):
        """Test task handles storage download errors."""
        mock_db = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_db
        mock_db.get.return_value = mock_ingestion

        mock_download.side_effect = Exception("Storage error")

        with pytest.raises(Exception, match="Storage error"):
            process_ocr_task(str(mock_ingestion.id))

        # Verify status was updated to FAILED
        assert mock_ingestion.status == ExtractionStatus.FAILED
        mock_db.commit.assert_called()

    @patch("app.tasks.extraction.settings")
    @patch("app.tasks.extraction.get_db_context")
    @patch("app.tasks.extraction.download_from_storage")
    @patch("app.tasks.extraction.MistralOCRProvider")
    def test_process_ocr_task_ocr_provider_error(
        self,
        mock_provider_class,
        mock_download,
        mock_db_context,
        mock_settings,
        mock_ingestion,
    ):
        """Test task handles OCR provider errors."""
        mock_settings.MISTRAL_API_KEY = "test-api-key"

        mock_db = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_db
        mock_db.get.return_value = mock_ingestion

        mock_download.return_value = b"%PDF-1.4 content"

        mock_provider = AsyncMock()
        mock_provider.extract_text.side_effect = OCRProviderError("API error")
        mock_provider_class.return_value = mock_provider

        with pytest.raises(OCRProviderError, match="API error"):
            process_ocr_task(str(mock_ingestion.id))

        # Verify status was updated to FAILED
        assert mock_ingestion.status == ExtractionStatus.FAILED
        mock_db.commit.assert_called()

    @patch("app.tasks.extraction.settings")
    @patch("app.tasks.extraction.get_db_context")
    @patch("app.tasks.extraction.download_from_storage")
    @patch("app.tasks.extraction.MistralOCRProvider")
    @patch("app.tasks.extraction.process_ocr_task.retry")
    def test_process_ocr_task_retries_on_failure(
        self,
        mock_retry,
        mock_provider_class,
        mock_download,
        mock_db_context,
        mock_settings,
        mock_ingestion,
    ):
        """Test task retries on transient failures."""
        mock_settings.MISTRAL_API_KEY = "test-api-key"

        mock_db = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_db
        mock_db.get.return_value = mock_ingestion

        mock_download.return_value = b"%PDF-1.4 content"

        mock_provider = AsyncMock()
        mock_provider.extract_text.side_effect = OCRProviderError("Rate limit exceeded")
        mock_provider_class.return_value = mock_provider

        mock_retry.side_effect = Retry()

        with pytest.raises(Retry):
            process_ocr_task(str(mock_ingestion.id))

        # Verify retry was called with exponential backoff
        mock_retry.assert_called_once()
        call_kwargs = mock_retry.call_args[1]
        assert "countdown" in call_kwargs
        assert call_kwargs["max_retries"] == 3

    @patch("app.tasks.extraction.get_db_context")
    @patch("app.tasks.extraction.download_from_storage")
    @patch("app.tasks.extraction.MistralOCRProvider")
    def test_process_ocr_task_invalid_ingestion_id(
        self, mock_provider_class, mock_download, mock_db_context
    ):
        """Test task handles invalid ingestion ID format."""
        with pytest.raises(ValueError, match="Invalid ingestion ID"):
            process_ocr_task("not-a-uuid")

    @patch("app.tasks.extraction.settings")
    @patch("app.tasks.extraction.get_db_context")
    @patch("app.tasks.extraction.download_from_storage")
    @patch("app.tasks.extraction.MistralOCRProvider")
    def test_process_ocr_task_updates_status_to_processing(
        self,
        mock_provider_class,
        mock_download,
        mock_db_context,
        mock_settings,
        mock_ingestion,
        mock_ocr_result,
    ):
        """Test task updates status to OCR_PROCESSING before starting OCR."""
        mock_settings.MISTRAL_API_KEY = "test-api-key"

        mock_db = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_db
        mock_db.get.return_value = mock_ingestion

        mock_download.return_value = b"%PDF-1.4 content"

        mock_provider = AsyncMock()
        mock_provider.extract_text.return_value = mock_ocr_result
        mock_provider_class.return_value = mock_provider

        # Track status changes
        status_changes = []

        def track_status_change(*args, **kwargs):
            status_changes.append(mock_ingestion.status)

        mock_db.commit.side_effect = track_status_change

        process_ocr_task(str(mock_ingestion.id))

        # Verify status progression: OCR_PROCESSING -> OCR_COMPLETE
        assert len(status_changes) >= 2
        assert ExtractionStatus.OCR_PROCESSING in status_changes
        assert status_changes[-1] == ExtractionStatus.OCR_COMPLETE
