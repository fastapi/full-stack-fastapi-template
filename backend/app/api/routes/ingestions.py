"""API routes for PDF worksheet upload and ingestion management."""

import logging
import uuid
from io import BytesIO
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from pypdf import PdfReader

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import Ingestion, IngestionPublic, IngestionsPublic
from app.services.storage import generate_presigned_url, upload_to_supabase
from app.tasks.extraction import process_ocr_task

router = APIRouter(prefix="/ingestions", tags=["ingestions"])

logger = logging.getLogger(__name__)

# File size limit: 25MB
MAX_FILE_SIZE = 25 * 1024 * 1024


@router.post("/", response_model=IngestionPublic, status_code=201)
async def create_ingestion(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(..., description="PDF worksheet file"),
) -> Any:
    """
    Upload PDF worksheet and create extraction record.

    Validates file type, size, uploads to Supabase Storage,
    extracts metadata, and creates extraction record.
    """
    # Validate MIME type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only PDF files are supported."
        )

    # Read file content
    file_bytes = await file.read()

    # Validate file size
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: 25MB. Your file: {len(file_bytes) / (1024 * 1024):.1f}MB.",
        )

    # Validate PDF magic number (%PDF-)
    if not file_bytes.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file. File signature does not match PDF format.",
        )

    # Extract PDF metadata (page count)
    page_count = None
    try:
        reader = PdfReader(BytesIO(file_bytes))
        page_count = len(reader.pages)
        logger.info(f"Extracted page count: {page_count} for file: {file.filename}")
    except Exception as e:
        # Log warning but allow upload to continue with NULL page_count
        logger.warning(
            f"Could not extract page count from PDF: {file.filename}. Error: {e}"
        )

    # Generate unique storage path
    extraction_id = uuid.uuid4()
    storage_path = f"{current_user.id}/{extraction_id}/original.pdf"

    # Upload to Supabase Storage with retry logic
    try:
        upload_to_supabase(storage_path, file_bytes, "application/pdf")
        logger.info(f"Uploaded file to Supabase: {storage_path}")
    except Exception as e:
        logger.error(f"Supabase upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed. Please try again.")

    # Generate presigned URL (7-day expiry)
    try:
        presigned_url = generate_presigned_url(storage_path)
    except Exception as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        # If presigned URL generation fails, we should probably rollback the upload
        # But for now, just fail with 500
        raise HTTPException(
            status_code=500,
            detail="Failed to generate access URL. Please contact support.",
        )

    # Create extraction record in database
    ingestion = Ingestion(
        id=extraction_id,
        owner_id=current_user.id,
        filename=file.filename or "unknown.pdf",
        file_size=len(file_bytes),
        page_count=page_count,
        mime_type="application/pdf",
        presigned_url=presigned_url,
        storage_path=storage_path,
    )

    try:
        session.add(ingestion)
        session.commit()
        session.refresh(ingestion)
        logger.info(f"Created extraction record: {ingestion.id}")

        # Trigger asynchronous OCR processing
        task = process_ocr_task.delay(str(ingestion.id))
        logger.info(f"Triggered OCR task {task.id} for ingestion {ingestion.id}")

    except Exception as e:
        logger.error(f"Database error: {e}")
        # TODO: Ideally should cleanup uploaded file from Supabase here
        raise HTTPException(
            status_code=500,
            detail="Failed to create extraction record. Please try again.",
        )

    return ingestion


@router.get("/", response_model=IngestionsPublic)
def read_ingestions(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List user's uploaded PDF worksheets with pagination.

    Returns paginated list of ingestions owned by the current user.
    """
    ingestions, count = crud.get_ingestions(
        session=session, owner_id=current_user.id, skip=skip, limit=limit
    )

    return IngestionsPublic(data=ingestions, count=count)


@router.get("/{id}", response_model=IngestionPublic)
def get_ingestion(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
) -> Any:
    """
    Get a single ingestion by ID.

    Returns ingestion details including presigned URL for PDF access.
    Only returns ingestions owned by the current user (403 if not owner).
    """
    ingestion = crud.get_ingestion(
        session=session, ingestion_id=id, owner_id=current_user.id
    )

    if not ingestion:
        raise HTTPException(
            status_code=404, detail="Ingestion not found or access denied."
        )

    return ingestion
