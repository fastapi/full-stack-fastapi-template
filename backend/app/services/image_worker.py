import asyncio
import logging
from typing import Dict, Any

from app.services.background_service import background_service, JobStatus
from app.services.s3_service import s3_service
from app.services.image_service import image_service
from app.models import Image, ImageVariant, ImageProcessingJob
from sqlmodel import Session

logger = logging.getLogger(__name__)


class ImageProcessingWorker:
    """Background worker for processing image uploads."""

    def __init__(self):
        self.running = False
        self.worker_id = f"image_worker_{id(self)}"

    async def start(self, poll_interval: int = 5):
        """
        Start the background worker.

        Args:
            poll_interval: Seconds between job polls
        """
        self.running = True
        logger.info(f"Image processing worker {self.worker_id} started")

        while self.running:
            try:
                # Get next job
                job = await background_service.get_next_job(timeout=poll_interval)

                if job:
                    await self.process_job(job)
                else:
                    # No job available, wait
                    await asyncio.sleep(poll_interval)

            except Exception as e:
                logger.error(f"Worker error: {str(e)}")
                await asyncio.sleep(poll_interval)

        logger.info(f"Image processing worker {self.worker_id} stopped")

    def stop(self):
        """Stop the background worker."""
        self.running = False

    async def process_job(self, job: Dict[str, Any]):
        """
        Process a single image processing job.

        Args:
            job: Job data dictionary
        """
        job_id = job.get('id')
        job_type = job.get('type')
        job_data = job.get('data', {})

        logger.info(f"Processing job {job_id} of type {job_type}")

        try:
            if job_type == 'process_image_variants':
                await self.process_image_variants(job_id, job_data)
            elif job_type == 'delete_image_files':
                await self.delete_image_files(job_id, job_data)
            else:
                await background_service.update_job_status(
                    job_id,
                    JobStatus.FAILED,
                    error_message=f"Unknown job type: {job_type}"
                )

        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")

            # Try to retry the job
            if await background_service.increment_retry(job_id):
                logger.info(f"Job {job_id} queued for retry")
            else:
                await background_service.update_job_status(
                    job_id,
                    JobStatus.FAILED,
                    error_message=f"Processing failed: {str(e)}"
                )

    async def process_image_variants(self, job_id: str, job_data: Dict[str, Any]):
        """
        Process image variants for uploaded image.

        Args:
            job_id: Job ID
            job_data: Job data containing image information
        """
        from app.core.db import get_db_session

        image_id = job_data.get('image_id')
        if not image_id:
            raise ValueError("Image ID is required")

        # Get database session
        from app.core.db import get_db_context
        with get_db_context() as db:
            try:
                # Get image record
                image = db.get(Image, image_id)
                if not image:
                    raise ValueError(f"Image {image_id} not found")

                logger.info(f"Processing variants for image {image_id}")

                # Download original image from S3
                try:
                    from botocore.exceptions import ClientError

                    response = s3_service.s3_client.get_object(
                        Bucket=image.s3_bucket,
                        Key=image.s3_key
                    )
                    original_content = response['Body'].read()

                except ClientError as e:
                    raise ValueError(f"Failed to download image from S3: {str(e)}")

                # Process image variants
                variant_configs = image_service.get_variant_configurations()
                variants = await image_service.process_image_variants(
                    original_content,
                    variant_configs
                )

                # Upload variants to S3 and create database records
                for variant in variants:
                    # Upload variant to S3
                    upload_result = await s3_service.upload_file(
                        file_content=variant['content'],
                        filename=f"{image.original_filename}_{variant['type']}.{variant['format']}",
                        content_type=f"image/{variant['format']}",
                        prefix=f"variants/{variant['type']}"
                    )

                    # Create variant record
                    image_variant = ImageVariant(
                        variant_type=variant['type'],
                        width=variant['width'],
                        height=variant['height'],
                        file_size=variant['file_size'],
                        s3_bucket=upload_result['s3_bucket'],
                        s3_key=upload_result['s3_key'],
                        s3_url=upload_result['s3_url'],
                        quality=variant['quality'],
                        format=variant['format'],
                        image_id=image.id
                    )

                    db.add(image_variant)

                # Update image processing status
                image.processing_status = "completed"
                db.add(image)

                # Update processing job status
                from sqlmodel import select
                processing_job = db.exec(
                    select(ImageProcessingJob).where(ImageProcessingJob.image_id == image_id)
                ).first()

                if processing_job:
                    processing_job.status = "completed"
                    db.add(processing_job)

                # Commit all changes
                db.commit()

                # Mark job as completed
                await background_service.update_job_status(
                    job_id,
                    JobStatus.COMPLETED,
                    result={
                        'image_id': image_id,
                        'variants_created': len(variants)
                    }
                )

                logger.info(f"Successfully processed {len(variants)} variants for image {image_id}")

            except Exception as e:
                db.rollback()

                # Update image status to failed
                image = db.get(Image, image_id)
                if image:
                    image.processing_status = "failed"
                    db.add(image)

                # Update processing job status
                from sqlmodel import select
                processing_job = db.exec(
                    select(ImageProcessingJob).where(ImageProcessingJob.image_id == image_id)
                ).first()

                if processing_job:
                    processing_job.status = "failed"
                    processing_job.error_message = str(e)
                    db.add(processing_job)

                db.commit()
                raise

    async def delete_image_files(self, job_id: str, job_data: Dict[str, Any]):
        """
        Delete image files from S3.

        Args:
            job_id: Job ID
            job_data: Job data containing file keys to delete
        """
        file_keys = job_data.get('file_keys', [])

        if not file_keys:
            logger.warning("No file keys provided for deletion")
            return

        deleted_count = 0
        errors = []

        for file_key in file_keys:
            try:
                success = await s3_service.delete_file(file_key)
                if success:
                    deleted_count += 1
                else:
                    errors.append(f"Failed to delete {file_key}")
            except Exception as e:
                errors.append(f"Error deleting {file_key}: {str(e)}")

        result = {
            'total_files': len(file_keys),
            'deleted_count': deleted_count,
            'errors': errors
        }

        if errors:
            await background_service.update_job_status(
                job_id,
                JobStatus.FAILED,
                result=result,
                error_message=f"Failed to delete {len(errors)} files"
            )
        else:
            await background_service.update_job_status(
                job_id,
                JobStatus.COMPLETED,
                result=result
            )

        logger.info(f"Deletion job completed: {deleted_count}/{len(file_keys)} files deleted")


# Global worker instance
image_worker = ImageProcessingWorker()


async def start_image_worker():
    """Start the image processing worker."""
    # Run worker in background task
    asyncio.create_task(image_worker.start())


def stop_image_worker():
    """Stop the image processing worker."""
    image_worker.stop()


# Job creation functions
async def enqueue_image_processing(image_id: str, delay: int = 0) -> str:
    """
    Enqueue image processing job.

    Args:
        image_id: ID of the image to process
        delay: Delay in seconds before processing starts

    Returns:
        Job ID
    """
    return await background_service.enqueue_job(
        job_type='process_image_variants',
        job_data={'image_id': image_id},
        delay=delay
    )


async def enqueue_image_deletion(file_keys: list[str], delay: int = 0) -> str:
    """
    Enqueue image deletion job.

    Args:
        file_keys: List of S3 file keys to delete
        delay: Delay in seconds before deletion starts

    Returns:
        Job ID
    """
    return await background_service.enqueue_job(
        job_type='delete_image_files',
        job_data={'file_keys': file_keys},
        delay=delay
    )