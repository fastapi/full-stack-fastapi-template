"""OCR service providers for text extraction from PDFs.

This module provides OCR provider implementations following a common interface.
Currently supports Mistral AI's Vision OCR API.
"""

import uuid
from datetime import datetime
from typing import Any

import httpx
from pydantic import BaseModel, Field


class OCRProviderError(Exception):
    """Base exception for OCR provider errors."""

    pass


class RetryableError(OCRProviderError):
    """Error that should trigger a retry (500, 502, 503, 504, 408).

    These are transient errors that may resolve with retry.
    """

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class NonRetryableError(OCRProviderError):
    """Error that should NOT be retried (400, 401, 403, 404).

    These are permanent errors that won't resolve with retry.
    """

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class RateLimitError(RetryableError):
    """429 Rate Limit error with optional Retry-After header.

    Indicates the API rate limit has been exceeded.
    The retry_after attribute contains seconds to wait (from Retry-After header).
    """

    def __init__(self, message: str, retry_after: int | None = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after  # Seconds to wait before retry


class BoundingBox(BaseModel):
    """Bounding box coordinates for content elements."""

    x: float = Field(..., description="X coordinate of top-left corner")
    y: float = Field(..., description="Y coordinate of top-left corner")
    width: float = Field(..., description="Width of the bounding box")
    height: float = Field(..., description="Height of the bounding box")


class ContentBlock(BaseModel):
    """A content block extracted from a PDF page.

    Represents text, equations, tables, or images with their layout information.
    """

    block_id: str = Field(..., description="Unique identifier for this content block")
    block_type: str = Field(
        ...,
        description="Type of content: text, equation, table, image, header, paragraph, list",
    )
    text: str = Field(..., description="Extracted text content")
    bbox: BoundingBox = Field(..., description="Bounding box coordinates")
    confidence: float = Field(..., ge=0.0, le=1.0, description="OCR confidence score")
    latex: str | None = Field(None, description="LaTeX representation for equations")
    table_structure: dict[str, Any] | None = Field(
        None, description="Table structure metadata (rows, columns, cells)"
    )
    image_description: str | None = Field(
        None, description="Description of image content"
    )
    # NEW: Fields for semantic block extraction and question segmentation
    markdown_content: str | None = Field(
        None, description="Markdown representation from Mistral API"
    )
    hierarchy_level: int | None = Field(
        None, description="Nesting depth (0 = top level)"
    )
    parent_block_id: str | None = Field(
        None, description="Parent block ID for nested structures"
    )


class OCRPageResult(BaseModel):
    """OCR results for a single page."""

    page_number: int = Field(..., description="Page number (1-indexed)")
    page_width: float = Field(..., description="Page width in points")
    page_height: float = Field(..., description="Page height in points")
    blocks: list[ContentBlock] = Field(
        default_factory=list, description="Content blocks on this page"
    )


class OCRResult(BaseModel):
    """Complete OCR extraction result for a PDF document."""

    extraction_id: uuid.UUID = Field(
        ..., description="Unique identifier for this extraction"
    )
    ocr_provider: str = Field(..., description="OCR provider used (e.g., 'mistral')")
    processed_at: datetime = Field(..., description="Timestamp of processing")
    total_pages: int = Field(..., description="Total number of pages processed")
    processing_time_seconds: float = Field(
        ..., description="Total processing time in seconds"
    )
    pages: list[OCRPageResult] = Field(
        default_factory=list, description="Per-page OCR results"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (cost, avg confidence, etc.)",
    )
    # NEW: Store raw Mistral response for debugging and future re-processing
    raw_mistral_response: dict[str, Any] | None = Field(
        None, description="Original Mistral API response"
    )


class MistralOCRProvider:
    """Mistral AI Vision OCR provider implementation.

    Uses Mistral's /v1/vision/ocr endpoint for PDF text extraction.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.mistral.ai/v1"):
        """Initialize Mistral OCR provider.

        Args:
            api_key: Mistral API key
            base_url: Mistral API base URL (default: https://api.mistral.ai/v1)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(60.0),
        )

    def _map_block_type(self, mistral_type: str) -> str:
        """Map Mistral's block type to semantic types for segmentation.

        Args:
            mistral_type: Block type from Mistral API (e.g., "heading", "text")

        Returns:
            Semantic block type (e.g., "header", "paragraph")
        """
        mapping = {
            "heading": "header",
            "text": "paragraph",
            "equation": "equation",
            "table": "table",
            "image": "image",
            "list": "list",
        }
        return mapping.get(mistral_type, "text")  # Default to "text" if unknown

    def _build_hierarchy(self, blocks: list[ContentBlock]) -> list[ContentBlock]:
        """Build hierarchical parent-child relationships between blocks.

        Args:
            blocks: List of content blocks with hierarchy_level set

        Returns:
            Same list with parent_block_id populated
        """
        parent_stack: list[ContentBlock] = []

        for block in blocks:
            level = block.hierarchy_level or 0

            # Pop stack until we find the parent level
            while parent_stack and (parent_stack[-1].hierarchy_level or 0) >= level:
                parent_stack.pop()

            # Set parent_block_id if we have a parent
            if parent_stack:
                block.parent_block_id = parent_stack[-1].block_id

            # Add current block to stack
            parent_stack.append(block)

        return blocks

    async def extract_text(self, pdf_bytes: bytes) -> OCRResult:
        """Extract text and layout from PDF bytes using Mistral OCR.

        Args:
            pdf_bytes: Raw PDF file bytes

        Returns:
            OCRResult containing extracted content and metadata

        Raises:
            OCRProviderError: If the API request fails
        """
        import time

        start_time = time.time()
        extraction_id = uuid.uuid4()

        try:
            # Call Mistral OCR API
            response = await self.client.post(
                f"{self.base_url}/vision/ocr",
                json={
                    "file": pdf_bytes.decode("latin1"),  # Base64 or raw bytes
                    "options": {
                        "extract_tables": True,
                        "extract_equations": True,
                        "extract_images": True,
                    },
                },
            )

            # Error classification based on HTTP status code
            if response.status_code == 429:
                # Rate limit - extract Retry-After header
                retry_after_header = response.headers.get("retry-after")
                retry_seconds = int(retry_after_header) if retry_after_header else None
                raise RateLimitError(
                    "Mistral API rate limit exceeded", retry_after=retry_seconds
                )

            elif response.status_code == 401:
                raise NonRetryableError(
                    "Mistral API authentication failed - check API key",
                    status_code=401,
                )

            elif response.status_code in (400, 403, 404):
                # Client errors - don't retry
                raise NonRetryableError(
                    f"Mistral API error: {response.status_code}",
                    status_code=response.status_code,
                )

            elif response.status_code in (500, 502, 503, 504, 408):
                # Server errors - retry
                raise RetryableError(
                    f"Mistral API server error: {response.status_code}",
                    status_code=response.status_code,
                )

            elif response.status_code != 200:
                # Unknown error - default to retryable for safety
                raise RetryableError(
                    f"Mistral API error: {response.status_code}",
                    status_code=response.status_code,
                )

            api_response = response.json()
            processing_time = time.time() - start_time

            # Transform Mistral response to our OCRResult format
            pages = []
            for page_data in api_response.get("pages", []):
                blocks = []

                # Process text blocks with semantic type mapping
                for text_block in page_data.get("text_blocks", []):
                    bbox_data = text_block["bbox"]
                    mistral_type = text_block.get("type")

                    # If no type provided, default to "text" (fallback/unknown type)
                    # If type is provided, map to semantic type
                    if mistral_type is None:
                        block_type = "text"  # Default fallback
                    else:
                        block_type = self._map_block_type(mistral_type)

                    block = ContentBlock(
                        block_id=f"blk_{uuid.uuid4().hex[:8]}",
                        block_type=block_type,
                        text=text_block["text"],
                        bbox=BoundingBox(
                            x=bbox_data["x"],
                            y=bbox_data["y"],
                            width=bbox_data["width"],
                            height=bbox_data["height"],
                        ),
                        confidence=text_block.get("confidence", 0.0),
                        latex=text_block.get("latex"),
                        table_structure=None,
                        image_description=None,
                        # NEW: Capture additional fields for segmentation
                        markdown_content=text_block.get("markdown"),
                        hierarchy_level=text_block.get("level"),
                        parent_block_id=None,  # Will be set by _build_hierarchy
                    )
                    blocks.append(block)

                # Process tables
                for table_data in page_data.get("tables", []):
                    bbox_data = table_data["bbox"]
                    block = ContentBlock(
                        block_id=f"tbl_{uuid.uuid4().hex[:8]}",
                        block_type="table",
                        text="[Table]",
                        bbox=BoundingBox(
                            x=bbox_data["x"],
                            y=bbox_data["y"],
                            width=bbox_data["width"],
                            height=bbox_data["height"],
                        ),
                        confidence=0.95,
                        latex=None,
                        table_structure={
                            "rows": table_data.get("rows"),
                            "columns": table_data.get("columns"),
                            "cells": table_data.get("cells", []),
                        },
                        image_description=None,
                        markdown_content=None,
                        hierarchy_level=None,
                        parent_block_id=None,
                    )
                    blocks.append(block)

                # Process images
                for image_data in page_data.get("images", []):
                    bbox_data = image_data["bbox"]
                    block = ContentBlock(
                        block_id=f"img_{uuid.uuid4().hex[:8]}",
                        block_type="image",
                        text="[Image]",
                        bbox=BoundingBox(
                            x=bbox_data["x"],
                            y=bbox_data["y"],
                            width=bbox_data["width"],
                            height=bbox_data["height"],
                        ),
                        confidence=0.90,
                        latex=None,
                        table_structure=None,
                        image_description=image_data.get("description"),
                        markdown_content=None,
                        hierarchy_level=None,
                        parent_block_id=None,
                    )
                    blocks.append(block)

                # Build hierarchy for blocks on this page
                blocks = self._build_hierarchy(blocks)

                page_result = OCRPageResult(
                    page_number=page_data["page_number"],
                    page_width=page_data.get("page_width", 612),
                    page_height=page_data.get("page_height", 792),
                    blocks=blocks,
                )
                pages.append(page_result)

            return OCRResult(
                extraction_id=extraction_id,
                ocr_provider="mistral",
                processed_at=datetime.utcnow(),
                total_pages=len(pages),
                processing_time_seconds=processing_time,
                pages=pages,
                metadata={
                    "cost_usd": 0.01 * len(pages),  # Placeholder cost
                    "average_confidence": 0.95,  # Placeholder
                },
                raw_mistral_response=api_response,  # Store raw API response
            )

        except httpx.HTTPStatusError as e:
            raise OCRProviderError(f"Mistral API error: {e}") from e
        except httpx.ConnectError as e:
            raise OCRProviderError(f"Mistral API error: Connection failed - {e}") from e
        except Exception as e:
            if isinstance(e, OCRProviderError):
                raise
            raise OCRProviderError(f"Mistral API error: {e}") from e
