import uuid
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks, Body
from fastapi.responses import JSONResponse
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Image, ImagePublic, ImagesPublic, ImageUpdate, Message,
    ImageVariantPublic, User, ImageCreate
)
from app.crud_image import (
    create_image, get_image, get_images, update_image, delete_image as crud_delete_image,
    get_image_variants, create_image_variants, get_processing_job,
    create_processing_job, get_user_image_stats, search_images_globally
)
from app.services.image_service import image_service
from app.services.s3_service import s3_service
from app.services.image_worker import enqueue_image_processing, enqueue_image_deletion

router = APIRouter(prefix="/images", tags=["images"])


@router.get("/", response_model=ImagesPublic)
def read_images(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    processing_status: Optional[str] = None
) -> Any:
    """
    Retrieve images with pagination and filtering.

    Args:
        session: Database session
        current_user: Current authenticated user
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Search term for filename, alt_text, description, or tags
        processing_status: Filter by processing status
    """
    if current_user.is_superuser and search:
        # Admin global search
        images, count = search_images_globally(
            session=session,
            query=search,
            skip=skip,
            limit=limit
        )
    else:
        # Regular user or admin personal search
        owner_id = None if current_user.is_superuser and not search else current_user.id
        images, count = get_images(
            session=session,
            owner_id=owner_id,
            skip=skip,
            limit=limit,
            search=search,
            processing_status=processing_status
        )

    return ImagesPublic(data=images, count=count)


@router.get("/stats", response_model=dict)
def read_image_stats(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get image statistics for the current user.
    """
    if not current_user.is_superuser:
        # Regular users can only see their own stats
        return get_user_image_stats(session=session, owner_id=current_user.id)
    else:
        # Admins can see global stats (simplified for now)
        # In a real application, you might want a separate global stats function
        return get_user_image_stats(session=session, owner_id=current_user.id)


@router.get("/{image_id}", response_model=ImagePublic)
def read_image(
    session: SessionDep,
    current_user: CurrentUser,
    image_id: uuid.UUID
) -> Any:
    """
    Get image by ID.
    """
    owner_id = None if current_user.is_superuser else current_user.id
    image = get_image(session=session, image_id=image_id, owner_id=owner_id)

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    return image


@router.get("/{image_id}/variants", response_model=list[ImageVariantPublic])
def read_image_variants(
    session: SessionDep,
    current_user: CurrentUser,
    image_id: uuid.UUID
) -> Any:
    """
    Get all variants for an image.
    """
    # Check image permissions first
    owner_id = None if current_user.is_superuser else current_user.id
    image = get_image(session=session, image_id=image_id, owner_id=owner_id)

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Get variants
    variants = get_image_variants(session=session, image_id=image_id)
    return variants


@router.post("/", response_model=ImagePublic)
async def upload_image(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    alt_text: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None)
) -> Any:
    """
    Upload a new image and start background processing.
    """
    # Validate file
    validation_result = await image_service.validate_upload_file(file)
    if not validation_result['is_valid']:
        raise HTTPException(
            status_code=400,
            detail=f"File validation failed: {'; '.join(validation_result['errors'])}"
        )

    try:
        # Read file content
        file_content = await file.read()
        await file.seek(0)  # Reset for potential re-reading

        # Get image dimensions
        width, height = await image_service.get_image_dimensions(file)

        # Generate safe filename
        safe_name = image_service.safe_filename(file.filename)

        # Upload to S3
        upload_result = await s3_service.upload_file(
            file_content=file_content,
            filename=safe_name,
            content_type=file.content_type,
            prefix="images"
        )

        # Create image record
        image_data = {
            "filename": safe_name,
            "original_filename": file.filename,
            "content_type": file.content_type,
            "file_size": upload_result['file_size'],
            "width": width,
            "height": height,
            "s3_bucket": upload_result['s3_bucket'],
            "s3_key": upload_result['s3_key'],
            "s3_url": upload_result['s3_url'],
            "processing_status": "pending",
            "alt_text": alt_text,
            "description": description,
            "tags": tags
        }

        image = create_image(
            session=session,
            image_in=ImageCreate.model_validate(image_data),
            owner_id=current_user.id
        )

        # Create processing job record
        processing_job = create_processing_job(
            session=session,
            image_id=image.id
        )

        # Enqueue background processing
        job_id = await enqueue_image_processing(image.id)

        # Note: job_id is for internal tracking, not returned to user

        return image

    except Exception as e:
        # If image was created but processing failed, clean it up
        if 'image' in locals():
            session.delete(image)
            session.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image upload: {str(e)}"
        )


@router.put("/{image_id}", response_model=ImagePublic)
def update_image_metadata(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    image_id: uuid.UUID,
    image_in: ImageUpdate
) -> Any:
    """
    Update image metadata (alt text, description, tags).
    """
    owner_id = None if current_user.is_superuser else current_user.id
    image = get_image(session=session, image_id=image_id, owner_id=owner_id)

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    updated_image = update_image(
        session=session,
        db_image=image,
        image_in=image_in
    )

    return updated_image


@router.delete("/{image_id}")
async def delete_image(
    session: SessionDep,
    current_user: CurrentUser,
    image_id: uuid.UUID,
    background_tasks: BackgroundTasks
) -> Message:
    """
    Delete an image and all its files from S3.
    """
    owner_id = None if current_user.is_superuser else current_user.id
    image = get_image(session=session, image_id=image_id, owner_id=owner_id)

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    try:
        # Collect all S3 keys to delete
        files_to_delete = [image.s3_key]

        # Get variants to delete their files too
        variants = get_image_variants(session=session, image_id=image_id)
        for variant in variants:
            files_to_delete.append(variant.s3_key)

        # Delete from database (this cascades to variants and processing jobs)
        deleted_image = crud_delete_image(
            session=session,
            image_id=image_id,
            owner_id=image.owner_id
        )

        # Enqueue background deletion of S3 files
        if files_to_delete:
            await enqueue_image_deletion(files_to_delete)

        return Message(message="Image deleted successfully")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete image: {str(e)}"
        )


@router.get("/{image_id}/processing-status")
def get_processing_status(
    session: SessionDep,
    current_user: CurrentUser,
    image_id: uuid.UUID
) -> Any:
    """
    Get the processing status of an image.
    """
    owner_id = None if current_user.is_superuser else current_user.id
    image = get_image(session=session, image_id=image_id, owner_id=owner_id)

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Get processing job
    processing_job = get_processing_job(session=session, image_id=image_id)

    # Get variants
    variants = get_image_variants(session=session, image_id=image_id)

    response = {
        "image_id": image_id,
        "processing_status": image.processing_status,
        "variants_created": len(variants),
        "variants": [
            {
                "type": variant.variant_type,
                "width": variant.width,
                "height": variant.height,
                "file_size": variant.file_size,
                "s3_url": variant.s3_url
            }
            for variant in variants
        ]
    }

    if processing_job:
        response.update({
            "job_status": processing_job.status,
            "retry_count": processing_job.retry_count,
            "error_message": processing_job.error_message
        })

    return response


@router.post("/{image_id}/retry-processing")
async def retry_image_processing(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    image_id: uuid.UUID,
    background_tasks: BackgroundTasks
) -> Message:
    """
    Retry processing for a failed image.
    """
    owner_id = None if current_user.is_superuser else current_user.id
    image = get_image(session=session, image_id=image_id, owner_id=owner_id)

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    if image.processing_status != "failed":
        raise HTTPException(
            status_code=400,
            detail="Only failed images can be retried"
        )

    try:
        # Reset image status
        image.processing_status = "pending"
        session.add(image)
        session.commit()

        # Create new processing job
        processing_job = create_processing_job(session=session, image_id=image_id)

        # Enqueue for processing
        await enqueue_image_processing(image.id)

        return Message(message="Image processing retry started")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retry image processing: {str(e)}"
        )


@router.post("/bulk-delete")
async def bulk_delete_images(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
    image_ids: list[uuid.UUID] = Body(..., embed=True)
) -> Any:
    """
    Delete multiple images in bulk.
    """
    if not image_ids:
        raise HTTPException(
            status_code=400,
            detail="No image IDs provided"
        )

    deleted_count = 0
    files_to_delete = []

    try:
        for image_id in image_ids:
            owner_id = None if current_user.is_superuser else current_user.id
            image = get_image(session=session, image_id=image_id, owner_id=owner_id)

            if image:
                # Collect S3 files for deletion
                files_to_delete.append(image.s3_key)
                variants = get_image_variants(session=session, image_id=image_id)
                for variant in variants:
                    files_to_delete.append(variant.s3_key)

                # Delete from database
                crud_delete_image(session=session, image_id=image_id, owner_id=image.owner_id)
                deleted_count += 1

        # Enqueue background deletion of S3 files
        if files_to_delete:
            await enqueue_image_deletion(files_to_delete)

        return {
            "message": f"Successfully deleted {deleted_count} images",
            "deleted_count": deleted_count,
            "total_requested": len(image_ids)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to bulk delete images: {str(e)}"
        )