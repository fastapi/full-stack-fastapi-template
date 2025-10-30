"""Tests for OCR service providers."""

import uuid
from datetime import datetime
from unittest.mock import Mock

import httpx
import pytest

from app.services.ocr import (
    BoundingBox,
    ContentBlock,
    MistralOCRProvider,
    OCRPageResult,
    OCRProviderError,
    OCRResult,
)


class TestMistralOCRProvider:
    """Test Mistral OCR provider implementation."""

    def test_mistral_ocr_provider_initialization(self):
        """Test that MistralOCRProvider initializes with API key."""
        provider = MistralOCRProvider(api_key="test-key-12345")
        assert provider.api_key == "test-key-12345"
        assert provider.base_url == "https://api.mistral.ai/v1"

    @pytest.mark.asyncio
    async def test_extract_text_success(self):
        """Test successful OCR extraction with mocked Mistral API response."""

        # Mock Mistral API response
        def mock_handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/vision/ocr"
            assert request.method == "POST"

            return httpx.Response(
                status_code=200,
                json={
                    "pages": [
                        {
                            "page_number": 1,
                            "text_blocks": [
                                {
                                    "text": "Solve for x: 2x + 5 = 15",
                                    "bbox": {
                                        "x": 100,
                                        "y": 200,
                                        "width": 300,
                                        "height": 50,
                                    },
                                    "confidence": 0.98,
                                    "type": "text",
                                }
                            ],
                            "tables": [],
                            "images": [],
                        }
                    ]
                },
            )

        # Create provider with mock transport
        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="test-key")
            provider.client = client

            # Test extraction
            pdf_bytes = b"%PDF-1.4 fake content"
            result = await provider.extract_text(pdf_bytes)

            # Verify result structure
            assert isinstance(result, OCRResult)
            assert result.ocr_provider == "mistral"
            assert result.total_pages == 1
            assert len(result.pages) == 1

            # Verify page content
            page = result.pages[0]
            assert page.page_number == 1
            assert len(page.blocks) == 1

            # Verify content block
            block = page.blocks[0]
            assert block.text == "Solve for x: 2x + 5 = 15"
            assert block.block_type == "text"
            assert block.confidence == 0.98
            assert block.bbox.x == 100
            assert block.bbox.y == 200

    @pytest.mark.asyncio
    async def test_extract_text_with_complex_content(self):
        """Test OCR extraction with tables, equations, and images."""

        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                status_code=200,
                json={
                    "pages": [
                        {
                            "page_number": 1,
                            "text_blocks": [
                                {
                                    "text": "Question 1",
                                    "bbox": {
                                        "x": 50,
                                        "y": 100,
                                        "width": 200,
                                        "height": 30,
                                    },
                                    "confidence": 0.99,
                                    "type": "header",
                                },
                                {
                                    "text": "$$2x + 5 = 15$$",
                                    "bbox": {
                                        "x": 100,
                                        "y": 260,
                                        "width": 200,
                                        "height": 40,
                                    },
                                    "confidence": 0.95,
                                    "type": "equation",
                                    "latex": "2x + 5 = 15",
                                },
                            ],
                            "tables": [
                                {
                                    "bbox": {
                                        "x": 50,
                                        "y": 320,
                                        "width": 300,
                                        "height": 100,
                                    },
                                    "rows": 2,
                                    "columns": 2,
                                    "cells": [
                                        {
                                            "row": 0,
                                            "col": 0,
                                            "text": "A.",
                                            "bbox": {
                                                "x": 50,
                                                "y": 320,
                                                "width": 50,
                                                "height": 50,
                                            },
                                        },
                                        {
                                            "row": 0,
                                            "col": 1,
                                            "text": "10",
                                            "bbox": {
                                                "x": 100,
                                                "y": 320,
                                                "width": 50,
                                                "height": 50,
                                            },
                                        },
                                    ],
                                }
                            ],
                            "images": [
                                {
                                    "bbox": {
                                        "x": 400,
                                        "y": 100,
                                        "width": 200,
                                        "height": 200,
                                    },
                                    "description": "Triangle diagram",
                                }
                            ],
                        }
                    ]
                },
            )

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="test-key")
            provider.client = client

            result = await provider.extract_text(b"%PDF-1.4 content")

            # Verify we have all content types
            page = result.pages[0]
            assert len(page.blocks) == 4  # header, equation, table, image

            # Find equation block
            equation_block = next(
                (b for b in page.blocks if b.block_type == "equation"), None
            )
            assert equation_block is not None
            assert equation_block.latex == "2x + 5 = 15"

            # Find table block
            table_block = next(
                (b for b in page.blocks if b.block_type == "table"), None
            )
            assert table_block is not None
            assert table_block.table_structure is not None
            assert table_block.table_structure["rows"] == 2

    @pytest.mark.asyncio
    async def test_extract_text_api_error_400(self):
        """Test handling of 400 Bad Request error."""

        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                status_code=400,
                json={"error": "Invalid file format"},
            )

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="test-key")
            provider.client = client

            with pytest.raises(OCRProviderError, match="Mistral API error"):
                await provider.extract_text(b"invalid content")

    @pytest.mark.asyncio
    async def test_extract_text_api_error_401(self):
        """Test handling of 401 Unauthorized error (invalid API key)."""

        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                status_code=401,
                json={"error": "Invalid API key"},
            )

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="invalid-key")
            provider.client = client

            with pytest.raises(OCRProviderError, match="Mistral API error"):
                await provider.extract_text(b"%PDF-1.4")

    @pytest.mark.asyncio
    async def test_extract_text_api_error_429(self):
        """Test handling of 429 Rate Limit error."""

        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                status_code=429,
                json={"error": "Rate limit exceeded"},
                headers={"Retry-After": "60"},
            )

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="test-key")
            provider.client = client

            with pytest.raises(OCRProviderError, match="Mistral API error"):
                await provider.extract_text(b"%PDF-1.4")

    @pytest.mark.asyncio
    async def test_extract_text_api_error_500(self):
        """Test handling of 500 Internal Server Error."""

        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                status_code=500,
                json={"error": "Internal server error"},
            )

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="test-key")
            provider.client = client

            with pytest.raises(OCRProviderError, match="Mistral API error"):
                await provider.extract_text(b"%PDF-1.4")

    @pytest.mark.asyncio
    async def test_extract_text_network_error(self):
        """Test handling of network/connection errors."""

        def mock_handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("Connection failed")

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="test-key")
            provider.client = client

            with pytest.raises(OCRProviderError, match="Mistral API error"):
                await provider.extract_text(b"%PDF-1.4")


class TestBoundingBox:
    """Test BoundingBox model."""

    def test_bounding_box_creation(self):
        """Test creating a bounding box."""
        bbox = BoundingBox(x=100, y=200, width=300, height=50)
        assert bbox.x == 100
        assert bbox.y == 200
        assert bbox.width == 300
        assert bbox.height == 50


class TestContentBlock:
    """Test ContentBlock model."""

    def test_content_block_text_type(self):
        """Test creating a text content block."""
        block = ContentBlock(
            block_id="blk_001",
            block_type="text",
            text="Sample text",
            bbox=BoundingBox(x=100, y=200, width=300, height=50),
            confidence=0.98,
        )
        assert block.block_type == "text"
        assert block.text == "Sample text"
        assert block.confidence == 0.98

    def test_content_block_equation_with_latex(self):
        """Test creating an equation block with LaTeX."""
        block = ContentBlock(
            block_id="blk_002",
            block_type="equation",
            text="$$2x + 5 = 15$$",
            bbox=BoundingBox(x=100, y=200, width=200, height=40),
            confidence=0.95,
            latex="2x + 5 = 15",
        )
        assert block.block_type == "equation"
        assert block.latex == "2x + 5 = 15"


class TestOCRResult:
    """Test OCRResult model."""

    def test_ocr_result_creation(self):
        """Test creating an OCR result."""
        extraction_id = uuid.uuid4()
        result = OCRResult(
            extraction_id=extraction_id,
            ocr_provider="mistral",
            processed_at=datetime.utcnow(),
            total_pages=1,
            processing_time_seconds=10.5,
            pages=[
                OCRPageResult(
                    page_number=1,
                    page_width=612,
                    page_height=792,
                    blocks=[],
                )
            ],
            metadata={"cost_usd": 0.01, "average_confidence": 0.95},
        )
        assert result.ocr_provider == "mistral"
        assert result.total_pages == 1
        assert result.metadata["cost_usd"] == 0.01
