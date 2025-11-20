import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional, Callable

from app.core.redis import redis_client
from app.core.config import settings


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class BackgroundJobService:
    """Background job processing service using Redis queues."""

    def __init__(self):
        self.queue_key = "background_jobs:queue"
        self.processing_key = "background_jobs:processing"
        self.results_key = "background_jobs:results"
        self.max_retries = 3
        self.retry_delay = 60  # seconds

    async def enqueue_job(
        self,
        job_type: str,
        job_data: Dict[str, Any],
        delay: int = 0,
        priority: int = 0
    ) -> str:
        """
        Enqueue a background job.

        Args:
            job_type: Type of job to execute
            job_data: Data required for the job
            delay: Delay in seconds before job is available
            priority: Job priority (higher = more priority)

        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        job = {
            'id': job_id,
            'type': job_type,
            'data': job_data,
            'status': JobStatus.PENDING,
            'created_at': datetime.utcnow().isoformat(),
            'delay_until': (datetime.utcnow() + timedelta(seconds=delay)).isoformat() if delay > 0 else None,
            'priority': priority,
            'retry_count': 0,
            'error_message': None
        }

        # Store job data
        redis_client.set(f"{self.results_key}:{job_id}", job, expire=86400)  # 24 hours

        # Add to queue
        queue_data = {
            'job_id': job_id,
            'priority': priority,
            'available_at': datetime.utcnow().timestamp() + delay
        }

        redis_client.client.zadd(self.queue_key, {json.dumps(queue_data): -priority})

        return job_id

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job status and details.

        Args:
            job_id: Job ID to check

        Returns:
            Job data or None if not found
        """
        return redis_client.get(f"{self.results_key}:{job_id}")

    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update job status.

        Args:
            job_id: Job ID to update
            status: New job status
            result: Job result data
            error_message: Error message if job failed

        Returns:
            True if updated successfully
        """
        job_data = redis_client.get(f"{self.results_key}:{job_id}")
        if not job_data:
            return False

        job_data['status'] = status
        job_data['updated_at'] = datetime.utcnow().isoformat()

        if result:
            job_data['result'] = result

        if error_message:
            job_data['error_message'] = error_message

        # Update job data
        redis_client.set(f"{self.results_key}:{job_id}", job_data, expire=86400)

        # If completed or failed, remove from queue
        if status in [JobStatus.COMPLETED, JobStatus.FAILED]:
            self._remove_from_queue(job_id)

        return True

    async def increment_retry(self, job_id: str) -> bool:
        """
        Increment job retry count.

        Args:
            job_id: Job ID to retry

        Returns:
            True if retry is allowed, False if max retries exceeded
        """
        job_data = redis_client.get(f"{self.results_key}:{job_id}")
        if not job_data:
            return False

        job_data['retry_count'] += 1

        if job_data['retry_count'] >= self.max_retries:
            # Max retries exceeded, mark as failed
            await self.update_job_status(
                job_id,
                JobStatus.FAILED,
                error_message=f"Max retries ({self.max_retries}) exceeded"
            )
            return False

        # Update retry count and re-queue with delay
        redis_client.set(f"{self.results_key}:{job_id}", job_data, expire=86400)

        # Re-queue with exponential backoff
        delay = self.retry_delay * (2 ** (job_data['retry_count'] - 1))
        await self.requeue_job(job_id, delay)

        return True

    async def requeue_job(self, job_id: str, delay: int = 0) -> bool:
        """
        Re-queue an existing job.

        Args:
            job_id: Job ID to re-queue
            delay: Delay in seconds before job is available

        Returns:
            True if re-queued successfully
        """
        job_data = redis_client.get(f"{self.results_key}:{job_id}")
        if not job_data:
            return False

        # Reset status to pending
        job_data['status'] = JobStatus.PENDING
        job_data['delay_until'] = (datetime.utcnow() + timedelta(seconds=delay)).isoformat() if delay > 0 else None

        redis_client.set(f"{self.results_key}:{job_id}", job_data, expire=86400)

        # Add back to queue
        queue_data = {
            'job_id': job_id,
            'priority': job_data.get('priority', 0),
            'available_at': datetime.utcnow().timestamp() + delay
        }

        redis_client.client.zadd(self.queue_key, {json.dumps(queue_data): -job_data.get('priority', 0)})

        return True

    def _remove_from_queue(self, job_id: str):
        """Remove job from active queue."""
        # Get all queue items and remove the one with matching job_id
        queue_items = redis_client.client.zrange(self.queue_key, 0, -1)
        for item in queue_items:
            try:
                queue_data = json.loads(item.decode('utf-8'))
                if queue_data.get('job_id') == job_id:
                    redis_client.client.zrem(self.queue_key, item)
                    break
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

    async def get_next_job(self, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """
        Get next available job from queue.

        Args:
            timeout: Timeout in seconds to wait for job

        Returns:
            Job data or None if no job available
        """
        current_time = datetime.utcnow().timestamp()

        # Get available jobs (sorted by priority and timestamp)
        available_jobs = redis_client.client.zrangebyscore(
            self.queue_key,
            0,
            current_time,
            start=0,
            num=1,
            withscores=True
        )

        if not available_jobs:
            return None

        # Get the highest priority job
        job_json, score = available_jobs[0]
        try:
            queue_data = json.loads(job_json.decode('utf-8'))
            job_id = queue_data.get('job_id')

            # Remove from queue and mark as processing
            redis_client.client.zrem(self.queue_key, job_json)

            # Get full job data
            job_data = redis_client.get(f"{self.results_key}:{job_id}")
            if job_data:
                await self.update_job_status(job_id, JobStatus.PROCESSING)
                return job_data

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            # Remove malformed job from queue
            redis_client.client.zrem(self.queue_key, job_json)
            logger.warning(f"Removed malformed job from queue: {e}")

        return None

    async def cleanup_old_jobs(self, days: int = 7) -> int:
        """
        Clean up old completed/failed jobs.

        Args:
            days: Age of jobs to clean up in days

        Returns:
            Number of jobs cleaned up
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        cleaned_count = 0

        # Get all job result keys
        result_keys = redis_client.client.keys(f"{self.results_key}:*")
        for key in result_keys:
            try:
                job_data = redis_client.get(key.decode('utf-8'))
                if not job_data:
                    continue

                # Check if job is old and completed/failed
                if job_data.get('status') in [JobStatus.COMPLETED, JobStatus.FAILED]:
                    updated_at = job_data.get('updated_at', job_data.get('created_at'))
                    if updated_at:
                        job_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                        if job_date < cutoff_date:
                            redis_client.delete(key.decode('utf-8'))
                            cleaned_count += 1

            except Exception as e:
                logger.warning(f"Error cleaning up job {key}: {e}")
                continue

        return cleaned_count

    def get_queue_stats(self) -> Dict[str, int]:
        """
        Get queue statistics.

        Returns:
            Dictionary with queue statistics
        """
        stats = {
            'pending': 0,
            'processing': 0,
            'completed': 0,
            'failed': 0
        }

        try:
            # Count jobs in queue
            stats['pending'] = redis_client.client.zcard(self.queue_key)

            # Count jobs by status in results
            result_keys = redis_client.client.keys(f"{self.results_key}:*")
            for key in result_keys:
                try:
                    job_data = redis_client.get(key.decode('utf-8'))
                    if job_data:
                        status = job_data.get('status', JobStatus.PENDING)
                        if status in stats:
                            stats[status] += 1
                except Exception:
                    continue

        except Exception as e:
            logger.error(f"Error getting queue stats: {e}")

        return stats


# Logger instance
logger = logging.getLogger(__name__)

# Global background job service instance
background_service = BackgroundJobService()


# Decorator for creating background jobs
def background_job(job_type: str, delay: int = 0):
    """
    Decorator to convert function into background job.

    Args:
        job_type: Type identifier for the job
        delay: Delay in seconds before job starts
    """
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # Create job data
            job_data = {
                'function': func.__name__,
                'args': args,
                'kwargs': kwargs,
                'module': func.__module__
            }

            # Enqueue job
            job_id = await background_service.enqueue_job(
                job_type=job_type,
                job_data=job_data,
                delay=delay
            )

            return job_id

        return wrapper
    return decorator