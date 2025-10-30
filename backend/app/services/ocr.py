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
    """Exception raised when OCR provider encounters an error."""

    pass


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
        ..., description="Type of content: text, equation, table, image, header"
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

            if response.status_code != 200:
                error_msg = f"Mistral API error (status {response.status_code})"
                try:
                    error_data = response.json()
                    error_msg += f": {error_data.get('error', 'Unknown error')}"
                except Exception:
                    pass
                raise OCRProviderError(error_msg)

            api_response = response.json()
            processing_time = time.time() - start_time

            # Transform Mistral response to our OCRResult format
            pages = []
            for page_data in api_response.get("pages", []):
                blocks = []

                # Process text blocks
                for text_block in page_data.get("text_blocks", []):
                    bbox_data = text_block["bbox"]
                    block = ContentBlock(
                        block_id=f"blk_{uuid.uuid4().hex[:8]}",
                        block_type=text_block.get("type", "text"),
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
                    )
                    blocks.append(block)

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
            )

        except httpx.HTTPStatusError as e:
            raise OCRProviderError(f"Mistral API error: {e}") from e
        except httpx.ConnectError as e:
            raise OCRProviderError(f"Mistral API error: Connection failed - {e}") from e
        except Exception as e:
            if isinstance(e, OCRProviderError):
                raise
            raise OCRProviderError(f"Mistral API error: {e}") from e
