import uuid
from typing import Any, Optional

from sqlmodel import Session, select, and_, or_, func

from app.models import Image, ImageCreate, ImageUpdate, ImageVariant, ImageProcessingJob


from sqlalchemy import case

def create_image(*, session: Session, image_in: ImageCreate, owner_id: uuid.UUID) -> Image:
    """
    Create a new image record.

    Args:
        session: Database session
        image_in: Image creation data
        owner_id: ID of the image owner

    Returns:
        Created image record
    """
    db_image = Image.model_validate(image_in, update={"owner_id": owner_id})
    session.add(db_image)
    session.commit()
    session.refresh(db_image)
    return db_image


def get_image(*, session: Session, image_id: uuid.UUID, owner_id: Optional[uuid.UUID] = None) -> Optional[Image]:
    """
    Get an image by ID.

    Args:
        session: Database session
        image_id: Image ID to retrieve
        owner_id: Optional owner ID for permission checking

    Returns:
        Image record or None if not found
    """
    statement = select(Image).where(Image.id == image_id)

    if owner_id:
        statement = statement.where(Image.owner_id == owner_id)

    return session.exec(statement).first()


def get_images(
    *,
    session: Session,
    owner_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    processing_status: Optional[str] = None
) -> tuple[list[Image], int]:
    """
    Get images with pagination and filtering.

    Args:
        session: Database session
        owner_id: ID of the owner (optional)
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Search term for filename, alt_text, description, or tags
        processing_status: Filter by processing status

    Returns:
        Tuple of (images list, total count)
    """
    # Build base query
    statement = select(Image)
    count_statement = select(func.count()).select_from(Image)

    if owner_id:
        statement = statement.where(Image.owner_id == owner_id)
        count_statement = count_statement.where(Image.owner_id == owner_id)

    # Apply filters
    if search:
        search_filter = or_(
            Image.filename.ilike(f"%{search}%"),
            Image.original_filename.ilike(f"%{search}%"),
            Image.alt_text.ilike(f"%{search}%"),
            Image.description.ilike(f"%{search}%"),
            Image.tags.ilike(f"%{search}%")
        )
        statement = statement.where(search_filter)
        count_statement = count_statement.where(search_filter)

    if processing_status:
        status_filter = Image.processing_status == processing_status
        statement = statement.where(status_filter)
        count_statement = count_statement.where(status_filter)

    # Get total count
    total_count = session.exec(count_statement).one()

    # Apply pagination and ordering
    statement = statement.order_by(Image.created_at.desc()).offset(skip).limit(limit)

    images = session.exec(statement).all()

    return images, total_count


def update_image(*, session: Session, db_image: Image, image_in: ImageUpdate) -> Image:
    """
    Update an image record.

    Args:
        session: Database session
        db_image: Existing image record
        image_in: Image update data

    Returns:
        Updated image record
    """
    image_data = image_in.model_dump(exclude_unset=True)
    db_image.sqlmodel_update(image_data)
    session.add(db_image)
    session.commit()
    session.refresh(db_image)
    return db_image


def delete_image(*, session: Session, image_id: uuid.UUID, owner_id: uuid.UUID) -> Optional[Image]:
    """
    Delete an image and all related records.

    Args:
        session: Database session
        image_id: ID of the image to delete
        owner_id: ID of the owner for permission checking

    Returns:
        Deleted image record or None if not found
    """
    # Get the image with ownership check
    statement = select(Image).where(and_(Image.id == image_id, Image.owner_id == owner_id))
    db_image = session.exec(statement).first()

    if not db_image:
        return None

    session.delete(db_image)
    session.commit()
    return db_image


def get_image_variants(*, session: Session, image_id: uuid.UUID) -> list[ImageVariant]:
    """
    Get all variants for an image.

    Args:
        session: Database session
        image_id: ID of the parent image

    Returns:
        List of image variants
    """
    statement = select(ImageVariant).where(ImageVariant.image_id == image_id).order_by(
        # Order by size: large, medium, thumb
        case(
            (ImageVariant.variant_type == 'large', 1),
            (ImageVariant.variant_type == 'medium', 2),
            (ImageVariant.variant_type == 'thumb', 3),
            else_=4
        )
    )

    return session.exec(statement).all()


def get_image_variant(*, session: Session, variant_id: uuid.UUID) -> Optional[ImageVariant]:
    """
    Get a specific image variant by ID.

    Args:
        session: Database session
        variant_id: ID of the variant

    Returns:
        Image variant or None if not found
    """
    statement = select(ImageVariant).where(ImageVariant.id == variant_id)
    return session.exec(statement).first()


def create_image_variants(*, session: Session, variants_data: list[dict]) -> list[ImageVariant]:
    """
    Create multiple image variants.

    Args:
        session: Database session
        variants_data: List of variant data dictionaries

    Returns:
        List of created image variants
    """
    variants = []
    for variant_data in variants_data:
        variant = ImageVariant.model_validate(variant_data)
        session.add(variant)
        variants.append(variant)

    session.commit()

    # Refresh all variants to get their IDs
    for variant in variants:
        session.refresh(variant)

    return variants


def get_processing_job(*, session: Session, image_id: uuid.UUID) -> Optional[ImageProcessingJob]:
    """
    Get the current processing job for an image.

    Args:
        session: Database session
        image_id: ID of the image

    Returns:
        Processing job or None if not found
    """
    statement = select(ImageProcessingJob).where(ImageProcessingJob.image_id == image_id)
    return session.exec(statement).first()


def create_processing_job(*, session: Session, image_id: uuid.UUID) -> ImageProcessingJob:
    """
    Create a new processing job for an image.

    Args:
        session: Database session
        image_id: ID of the image

    Returns:
        Created processing job
    """
    processing_job = ImageProcessingJob(
        image_id=image_id,
        status="pending",
        retry_count=0
    )

    session.add(processing_job)
    session.commit()
    session.refresh(processing_job)
    return processing_job


def update_processing_job(
    *,
    session: Session,
    job_id: uuid.UUID,
    status: str,
    error_message: Optional[str] = None
) -> Optional[ImageProcessingJob]:
    """
    Update a processing job status.

    Args:
        session: Database session
        job_id: ID of the job to update
        status: New status
        error_message: Optional error message

    Returns:
        Updated processing job or None if not found
    """
    statement = select(ImageProcessingJob).where(ImageProcessingJob.id == job_id)
    job = session.exec(statement).first()

    if not job:
        return None

    job.status = status
    if error_message:
        job.error_message = error_message

    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def get_user_image_stats(*, session: Session, owner_id: uuid.UUID) -> dict:
    """
    Get image statistics for a user.

    Args:
        session: Database session
        owner_id: ID of the user

    Returns:
        Dictionary with image statistics
    """
    # Count total images
    total_count = session.exec(
        select(func.count()).select_from(Image).where(Image.owner_id == owner_id)
    ).one()

    # Count by processing status
    status_counts = session.exec(
        select(Image.processing_status, func.count())
        .select_from(Image)
        .where(Image.owner_id == owner_id)
        .group_by(Image.processing_status)
    ).all()

    # Calculate total file size
    total_size = session.exec(
        select(func.sum(Image.file_size))
        .select_from(Image)
        .where(Image.owner_id == owner_id)
    ).one() or 0

    return {
        "total_images": total_count,
        "total_file_size": total_size,
        "processing_status_counts": dict(status_counts),
        "average_file_size": total_size / max(total_count, 1)
    }


def search_images_globally(
    *,
    session: Session,
    query: str,
    skip: int = 0,
    limit: int = 20,
    owner_id: Optional[uuid.UUID] = None
) -> tuple[list[Image], int]:
    """
    Global image search across all users (admin function).

    Args:
        session: Database session
        query: Search query
        skip: Number of records to skip
        limit: Maximum number of records to return
        owner_id: Optional owner filter

    Returns:
        Tuple of (images list, total count)
    """
    # Build search filter
    search_filter = or_(
        Image.filename.ilike(f"%{query}%"),
        Image.original_filename.ilike(f"%{query}%"),
        Image.alt_text.ilike(f"%{query}%"),
        Image.description.ilike(f"%{query}%"),
        Image.tags.ilike(f"%{query}%")
    )

    # Build base query
    statement = select(Image).where(search_filter)
    count_statement = select(func.count()).select_from(Image).where(search_filter)

    # Apply owner filter if specified
    if owner_id:
        statement = statement.where(Image.owner_id == owner_id)
        count_statement = count_statement.where(Image.owner_id == owner_id)

    # Get total count
    total_count = session.exec(count_statement).one()

    # Apply pagination and ordering
    statement = statement.order_by(Image.created_at.desc()).offset(skip).limit(limit)

    images = session.exec(statement).all()

    return images, total_count