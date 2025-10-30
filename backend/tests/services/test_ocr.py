"""Tests for OCR service providers."""

import uuid
from datetime import datetime

import httpx
import pytest

from app.services.ocr import (
    BoundingBox,
    ContentBlock,
    MistralOCRProvider,
    NonRetryableError,
    OCRPageResult,
    OCRProviderError,
    OCRResult,
    RateLimitError,
    RetryableError,
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
            assert block.block_type == "paragraph"  # "text" type maps to "paragraph"
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
        """Test handling of 400 Bad Request error raises NonRetryableError."""

        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                status_code=400,
                json={"error": "Invalid file format"},
            )

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="test-key")
            provider.client = client

            with pytest.raises(NonRetryableError) as exc_info:
                await provider.extract_text(b"invalid content")

            assert exc_info.value.status_code == 400
            assert "400" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_extract_text_api_error_401(self):
        """Test handling of 401 Unauthorized error raises NonRetryableError."""

        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                status_code=401,
                json={"error": "Invalid API key"},
            )

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="invalid-key")
            provider.client = client

            with pytest.raises(NonRetryableError) as exc_info:
                await provider.extract_text(b"%PDF-1.4")

            assert exc_info.value.status_code == 401
            assert "authentication" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_extract_text_api_error_429(self):
        """Test handling of 429 Rate Limit error raises RateLimitError with retry_after."""

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

            with pytest.raises(RateLimitError) as exc_info:
                await provider.extract_text(b"%PDF-1.4")

            assert exc_info.value.status_code == 429
            assert exc_info.value.retry_after == 60
            assert "rate limit" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_extract_text_api_error_500(self):
        """Test handling of 500 Internal Server Error raises RetryableError."""

        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                status_code=500,
                json={"error": "Internal server error"},
            )

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="test-key")
            provider.client = client

            with pytest.raises(RetryableError) as exc_info:
                await provider.extract_text(b"%PDF-1.4")

            assert exc_info.value.status_code == 500
            assert "500" in str(exc_info.value)

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

    @pytest.mark.asyncio
    async def test_extract_text_api_error_429_without_retry_after(self):
        """Test 429 error without Retry-After header defaults retry_after to None."""

        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                status_code=429,
                json={"error": "Rate limit exceeded"},
                # No Retry-After header
            )

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="test-key")
            provider.client = client

            with pytest.raises(RateLimitError) as exc_info:
                await provider.extract_text(b"%PDF-1.4")

            assert exc_info.value.status_code == 429
            assert exc_info.value.retry_after is None

    @pytest.mark.asyncio
    async def test_extract_text_api_error_502(self):
        """Test 502 Bad Gateway raises RetryableError."""

        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(status_code=502)

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="test-key")
            provider.client = client

            with pytest.raises(RetryableError) as exc_info:
                await provider.extract_text(b"%PDF-1.4")

            assert exc_info.value.status_code == 502

    @pytest.mark.asyncio
    async def test_extract_text_api_error_503(self):
        """Test 503 Service Unavailable raises RetryableError."""

        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(status_code=503)

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="test-key")
            provider.client = client

            with pytest.raises(RetryableError) as exc_info:
                await provider.extract_text(b"%PDF-1.4")

            assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_extract_text_api_error_403(self):
        """Test 403 Forbidden raises NonRetryableError."""

        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(status_code=403)

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="test-key")
            provider.client = client

            with pytest.raises(NonRetryableError) as exc_info:
                await provider.extract_text(b"%PDF-1.4")

            assert exc_info.value.status_code == 403


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


class TestSemanticBlockExtraction:
    """Test semantic block extraction features for question segmentation."""

    @pytest.mark.asyncio
    async def test_semantic_block_type_classification(self):
        """Test that blocks are correctly classified with semantic types."""

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
                                    "type": "heading",
                                    "bbox": {
                                        "x": 50,
                                        "y": 100,
                                        "width": 200,
                                        "height": 30,
                                    },
                                    "confidence": 0.99,
                                },
                                {
                                    "text": "Round 3.456 to 1 decimal place.",
                                    "type": "text",
                                    "bbox": {
                                        "x": 50,
                                        "y": 140,
                                        "width": 500,
                                        "height": 50,
                                    },
                                    "confidence": 0.97,
                                },
                                {
                                    "text": "$$\\frac{3x + 2}{5} = 7$$",
                                    "type": "equation",
                                    "latex": "\\frac{3x + 2}{5} = 7",
                                    "bbox": {
                                        "x": 50,
                                        "y": 200,
                                        "width": 200,
                                        "height": 40,
                                    },
                                    "confidence": 0.95,
                                },
                            ],
                            "tables": [],
                            "images": [],
                        }
                    ]
                },
            )

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="test-key")
            provider.client = client

            result = await provider.extract_text(b"%PDF-1.4 content")

            # Verify semantic block types are correctly mapped
            blocks = result.pages[0].blocks
            assert len(blocks) == 3

            # Check header block (heading → header)
            header_block = blocks[0]
            assert header_block.block_type == "header"
            assert header_block.text == "Question 1"

            # Check paragraph block (text → paragraph)
            paragraph_block = blocks[1]
            assert paragraph_block.block_type == "paragraph"
            assert "Round 3.456" in paragraph_block.text

            # Check equation block
            equation_block = blocks[2]
            assert equation_block.block_type == "equation"
            assert equation_block.latex == "\\frac{3x + 2}{5} = 7"

    @pytest.mark.asyncio
    async def test_table_structure_extraction_with_cells(self):
        """Test table extraction with cell-level row/column detail."""

        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                status_code=200,
                json={
                    "pages": [
                        {
                            "page_number": 1,
                            "text_blocks": [],
                            "tables": [
                                {
                                    "bbox": {
                                        "x": 50,
                                        "y": 200,
                                        "width": 300,
                                        "height": 100,
                                    },
                                    "rows": 4,
                                    "columns": 2,
                                    "cells": [
                                        {
                                            "row": 0,
                                            "col": 0,
                                            "text": "A.",
                                            "bbox": {
                                                "x": 50,
                                                "y": 200,
                                                "width": 50,
                                                "height": 25,
                                            },
                                        },
                                        {
                                            "row": 0,
                                            "col": 1,
                                            "text": "3.4",
                                            "bbox": {
                                                "x": 100,
                                                "y": 200,
                                                "width": 100,
                                                "height": 25,
                                            },
                                        },
                                        {
                                            "row": 1,
                                            "col": 0,
                                            "text": "B.",
                                            "bbox": {
                                                "x": 50,
                                                "y": 225,
                                                "width": 50,
                                                "height": 25,
                                            },
                                        },
                                        {
                                            "row": 1,
                                            "col": 1,
                                            "text": "3.5",
                                            "bbox": {
                                                "x": 100,
                                                "y": 225,
                                                "width": 100,
                                                "height": 25,
                                            },
                                        },
                                    ],
                                }
                            ],
                            "images": [],
                        }
                    ]
                },
            )

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="test-key")
            provider.client = client

            result = await provider.extract_text(b"%PDF-1.4 content")

            # Find table block
            table_block = next(
                (b for b in result.pages[0].blocks if b.block_type == "table"), None
            )
            assert table_block is not None

            # Verify table structure with cell-level detail
            table_struct = table_block.table_structure
            assert table_struct is not None
            assert table_struct["rows"] == 4
            assert table_struct["columns"] == 2
            assert len(table_struct["cells"]) == 4

            # Verify cell data with row/column positions
            cell_a = table_struct["cells"][0]
            assert cell_a["row"] == 0
            assert cell_a["col"] == 0
            assert cell_a["text"] == "A."

            cell_b = table_struct["cells"][2]
            assert cell_b["row"] == 1
            assert cell_b["col"] == 0
            assert cell_b["text"] == "B."

    @pytest.mark.asyncio
    async def test_hierarchical_structure_preservation(self):
        """Test that hierarchical structure (parent-child) is preserved."""

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
                                    "type": "heading",
                                    "bbox": {
                                        "x": 50,
                                        "y": 100,
                                        "width": 200,
                                        "height": 30,
                                    },
                                    "confidence": 0.99,
                                    "level": 0,
                                },
                                {
                                    "text": "(a) Find the value of x",
                                    "type": "list",
                                    "bbox": {
                                        "x": 70,
                                        "y": 140,
                                        "width": 400,
                                        "height": 30,
                                    },
                                    "confidence": 0.97,
                                    "level": 1,
                                },
                                {
                                    "text": "(b) Calculate the area",
                                    "type": "list",
                                    "bbox": {
                                        "x": 70,
                                        "y": 180,
                                        "width": 400,
                                        "height": 30,
                                    },
                                    "confidence": 0.97,
                                    "level": 1,
                                },
                            ],
                            "tables": [],
                            "images": [],
                        }
                    ]
                },
            )

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="test-key")
            provider.client = client

            result = await provider.extract_text(b"%PDF-1.4 content")

            blocks = result.pages[0].blocks
            assert len(blocks) == 3

            # Verify hierarchy levels are captured
            header_block = blocks[0]
            assert header_block.hierarchy_level == 0
            assert header_block.parent_block_id is None

            # Verify child blocks have parent references
            part_a = blocks[1]
            assert part_a.hierarchy_level == 1
            assert part_a.parent_block_id == header_block.block_id

            part_b = blocks[2]
            assert part_b.hierarchy_level == 1
            assert part_b.parent_block_id == header_block.block_id

    @pytest.mark.asyncio
    async def test_markdown_content_preservation(self):
        """Test that Mistral's Markdown output is preserved in blocks."""

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
                                    "type": "heading",
                                    "bbox": {
                                        "x": 50,
                                        "y": 100,
                                        "width": 200,
                                        "height": 30,
                                    },
                                    "confidence": 0.99,
                                    "markdown": "# Question 1",
                                },
                                {
                                    "text": "Solve the equation",
                                    "type": "text",
                                    "bbox": {
                                        "x": 50,
                                        "y": 140,
                                        "width": 300,
                                        "height": 30,
                                    },
                                    "confidence": 0.97,
                                    "markdown": "Solve the equation",
                                },
                            ],
                            "tables": [],
                            "images": [],
                        }
                    ]
                },
            )

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="test-key")
            provider.client = client

            result = await provider.extract_text(b"%PDF-1.4 content")

            blocks = result.pages[0].blocks

            # Verify markdown content is preserved
            header_block = blocks[0]
            assert header_block.markdown_content == "# Question 1"

            text_block = blocks[1]
            assert text_block.markdown_content == "Solve the equation"

    @pytest.mark.asyncio
    async def test_raw_mistral_response_storage(self):
        """Test that raw Mistral API response is stored for debugging."""

        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                status_code=200,
                json={
                    "pages": [
                        {
                            "page_number": 1,
                            "text_blocks": [
                                {
                                    "text": "Sample text",
                                    "type": "text",
                                    "bbox": {
                                        "x": 100,
                                        "y": 200,
                                        "width": 300,
                                        "height": 50,
                                    },
                                    "confidence": 0.98,
                                }
                            ],
                            "tables": [],
                            "images": [],
                        }
                    ],
                    "metadata": {"model": "mistral-ocr-v1", "api_version": "2025-01"},
                },
            )

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="test-key")
            provider.client = client

            result = await provider.extract_text(b"%PDF-1.4 content")

            # Verify raw response is stored
            assert result.raw_mistral_response is not None
            assert "pages" in result.raw_mistral_response
            assert "metadata" in result.raw_mistral_response
            assert result.raw_mistral_response["metadata"]["model"] == "mistral-ocr-v1"

    @pytest.mark.asyncio
    async def test_missing_block_type_defaults_to_text(self):
        """Test that blocks without type default to 'text' with warning."""

        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                status_code=200,
                json={
                    "pages": [
                        {
                            "page_number": 1,
                            "text_blocks": [
                                {
                                    "text": "Unknown block",
                                    # Missing "type" field
                                    "bbox": {
                                        "x": 100,
                                        "y": 200,
                                        "width": 300,
                                        "height": 50,
                                    },
                                    "confidence": 0.90,
                                }
                            ],
                            "tables": [],
                            "images": [],
                        }
                    ]
                },
            )

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = MistralOCRProvider(api_key="test-key")
            provider.client = client

            result = await provider.extract_text(b"%PDF-1.4 content")

            # Verify missing type defaults to "text"
            block = result.pages[0].blocks[0]
            assert block.block_type == "text"
            assert block.text == "Unknown block"
