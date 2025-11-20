import asyncio
import json
import uuid
from unittest.mock import MagicMock, AsyncMock, patch
import pytest

from app.services.background_service import BackgroundJobService, JobStatus


class TestBackgroundService:
    """Test suite for BackgroundJobService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = BackgroundJobService()

    @pytest.mark.asyncio
    @patch('app.services.background_service.redis_client')
    async def test_enqueue_job(self, mock_redis):
        """Test enqueuing a background job."""
        mock_redis.set.return_value = True
        mock_redis.client.zadd.return_value = 1

        job_type = "test_job"
        job_data = {"test_param": "test_value"}

        job_id = await self.service.enqueue_job(job_type=job_type, job_data=job_data)

        # Verify job ID format
        assert job_id is not None
        assert len(job_id) == 36  # UUID length

        # Verify job was stored in Redis
        mock_redis.set.assert_called()
        call_args = mock_redis.set.call_args
        stored_job = call_args[0][1]  # Second argument (the job object)

        assert stored_job['type'] == job_type
        assert stored_job['data'] == job_data
        assert stored_job['status'] == JobStatus.PENDING
        assert stored_job['priority'] == 0
        assert stored_job['retry_count'] == 0

        # Verify job was added to queue
        mock_redis.client.zadd.assert_called()

    @pytest.mark.asyncio
    @patch('app.services.background_service.redis_client')
    async def test_enqueue_job_with_delay_and_priority(self, mock_redis):
        """Test enqueuing a job with delay and priority."""
        mock_redis.set.return_value = True
        mock_redis.client.zadd.return_value = 1

        job_type = "priority_job"
        job_data = {"urgent": True}
        delay = 60
        priority = 5

        job_id = await self.service.enqueue_job(
            job_type=job_type,
            job_data=job_data,
            delay=delay,
            priority=priority
        )

        call_args = mock_redis.set.call_args
        stored_job = call_args[0][1]

        assert stored_job['delay_until'] is not None
        assert stored_job['priority'] == priority

    @pytest.mark.asyncio
    @patch('app.services.background_service.redis_client')
    async def test_get_job_status(self, mock_redis):
        """Test getting job status."""
        job_id = str(uuid.uuid4())
        expected_job = {
            'id': job_id,
            'type': 'test_job',
            'status': JobStatus.COMPLETED,
            'result': {'success': True}
        }

        mock_redis.get.return_value = expected_job

        result = await self.service.get_job_status(job_id)

        assert result == expected_job
        mock_redis.get.assert_called_once_with(f"background_jobs:results:{job_id}")

    @pytest.mark.asyncio
    @patch('app.services.background_service.redis_client')
    async def test_get_job_status_not_found(self, mock_redis):
        """Test getting status for non-existent job."""
        mock_redis.get.return_value = None

        job_id = str(uuid.uuid4())
        result = await self.service.get_job_status(job_id)

        assert result is None
        mock_redis.get.assert_called_once_with(f"background_jobs:results:{job_id}")

    @pytest.mark.asyncio
    @patch('app.services.background_service.redis_client')
    async def test_update_job_status(self, mock_redis):
        """Test updating job status."""
        job_id = str(uuid.uuid4())
        existing_job = {
            'id': job_id,
            'type': 'test_job',
            'status': JobStatus.PENDING,
            'data': {'param': 'value'}
        }

        mock_redis.get.return_value = existing_job
        mock_redis.set.return_value = True

        result = await self.service.update_job_status(
            job_id,
            JobStatus.COMPLETED,
            result={'output': 'success'}
        )

        assert result is True

        # Verify the job was updated
        call_args = mock_redis.set.call_args
        updated_job = call_args[0][1]

        assert updated_job['status'] == JobStatus.COMPLETED
        assert updated_job['result'] == {'output': 'success'}
        assert updated_job['data'] == {'param': 'value'}  # Original data preserved

    @pytest.mark.asyncio
    @patch('app.services.background_service.redis_client')
    async def test_update_job_status_with_error(self, mock_redis):
        """Test updating job status with error message."""
        job_id = str(uuid.uuid4())
        existing_job = {
            'id': job_id,
            'type': 'test_job',
            'status': JobStatus.PROCESSING
        }

        mock_redis.get.return_value = existing_job
        mock_redis.set.return_value = True

        error_message = "Processing failed due to timeout"
        result = await self.service.update_job_status(
            job_id,
            JobStatus.FAILED,
            error_message=error_message
        )

        assert result is True

        call_args = mock_redis.set.call_args
        updated_job = call_args[0][1]

        assert updated_job['status'] == JobStatus.FAILED
        assert updated_job['error_message'] == error_message

    @pytest.mark.asyncio
    @patch('app.services.background_service.redis_client')
    async def test_update_job_status_not_found(self, mock_redis):
        """Test updating status for non-existent job."""
        mock_redis.get.return_value = None

        job_id = str(uuid.uuid4())
        result = await self.service.update_job_status(job_id, JobStatus.COMPLETED)

        assert result is False

    @pytest.mark.asyncio
    @patch('app.services.background_service.redis_client')
    async def test_increment_retry(self, mock_redis):
        """Test incrementing job retry count."""
        job_id = str(uuid.uuid4())
        existing_job = {
            'id': job_id,
            'type': 'test_job',
            'status': JobStatus.FAILED,
            'retry_count': 1
        }

        mock_redis.get.return_value = existing_job
        mock_redis.set.return_value = True
        mock_redis.client.zadd.return_value = 1

        result = await self.service.increment_retry(job_id)

        assert result is True

        # Verify retry count was incremented
        call_args = mock_redis.set.call_args
        updated_job = call_args[0][1]

        assert updated_job['retry_count'] == 2
        assert updated_job['status'] == JobStatus.PENDING

        # Verify job was re-queued
        mock_redis.client.zadd.assert_called()

    @pytest.mark.asyncio
    @patch('app.services.background_service.redis_client')
    async def test_increment_retry_max_retries_exceeded(self, mock_redis):
        """Test increment retry when max retries exceeded."""
        job_id = str(uuid.uuid4())
        existing_job = {
            'id': job_id,
            'type': 'test_job',
            'status': JobStatus.FAILED,
            'retry_count': 3  # Already at max
        }

        mock_redis.get.return_value = existing_job
        mock_redis.set.return_value = True

        result = await self.service.increment_retry(job_id)

        assert result is False

        # Verify job was marked as failed
        call_args = mock_redis.set.call_args
        updated_job = call_args[0][1]

        assert updated_job['status'] == JobStatus.FAILED
        assert updated_job['retry_count'] == 4  # Incremented before check

    @pytest.mark.asyncio
    @patch('app.services.background_service.redis_client')
    async def test_increment_retry_not_found(self, mock_redis):
        """Test increment retry for non-existent job."""
        mock_redis.get.return_value = None

        job_id = str(uuid.uuid4())
        result = await self.service.increment_retry(job_id)

        assert result is False

    @pytest.mark.asyncio
    @patch('app.services.background_service.redis_client')
    async def test_requeue_job(self, mock_redis):
        """Test re-queuing an existing job."""
        job_id = str(uuid.uuid4())
        existing_job = {
            'id': job_id,
            'type': 'test_job',
            'status': JobStatus.FAILED,
            'priority': 2
        }

        mock_redis.get.return_value = existing_job
        mock_redis.set.return_value = True
        mock_redis.client.zadd.return_value = 1

        result = await self.service.requeue_job(job_id, delay=30)

        assert result is True

        # Verify job was re-queued with updated status
        call_args = mock_redis.set.call_args
        updated_job = call_args[0][1]

        assert updated_job['status'] == JobStatus.PENDING

        # Verify delay was set
        import datetime
        delay_until = datetime.datetime.fromisoformat(updated_job['delay_until'])
        # Should be approximately 30 seconds in the future
        import time
        time_diff = (delay_until - datetime.datetime.utcnow()).total_seconds()
        assert 25 <= time_diff <= 35  # Allow some tolerance

    @pytest.mark.asyncio
    @patch('app.services.background_service.redis_client')
    async def test_get_next_job(self, mock_redis):
        """Test getting next job from queue."""
        job_id = str(uuid.uuid4())
        job_data = {
            'id': job_id,
            'type': 'test_job',
            'data': {'param': 'value'}
        }

        # Mock Redis queue operations
        mock_redis.client.zrangebyscore.return_value = [
            (json.dumps({'job_id': job_id, 'priority': 0, 'available_at': 1234567890}).encode('utf-8'), 0)
        ]
        mock_redis.client.zrem.return_value = 1
        mock_redis.get.return_value = job_data

        result = await self.service.get_next_job()

        assert result is not None
        assert result['id'] == job_id
        assert result['type'] == 'test_job'
        assert result['data'] == {'param': 'value'}

        # Verify queue operations
        mock_redis.client.zrangebyscore.assert_called_once()
        mock_redis.client.zrem.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.background_service.redis_client')
    async def test_get_next_job_empty_queue(self, mock_redis):
        """Test getting next job when queue is empty."""
        mock_redis.client.zrangebyscore.return_value = []

        result = await self.service.get_next_job()

        assert result is None

    @pytest.mark.asyncio
    @patch('app.services.background_service.redis_client')
    async def test_cleanup_old_jobs(self, mock_redis):
        """Test cleaning up old completed/failed jobs."""
        # Mock Redis keys operation
        old_job_key = "background_jobs:results:old-job-id"
        recent_job_key = "background_jobs:results:recent-job-id"

        mock_redis.client.keys.return_value = [old_job_key.encode(), recent_job_key.encode()]

        # Mock job data
        old_job_data = {
            'status': JobStatus.COMPLETED,
            'updated_at': '2023-01-01T00:00:00'  # Old date
        }

        recent_job_data = {
            'status': JobStatus.FAILED,
            'updated_at': '2025-11-19T12:00:00'  # Recent date
        }

        def mock_get_side_effect(key):
            if old_job_key in str(key):
                return old_job_data
            elif recent_job_key in str(key):
                return recent_job_data
            return None

        mock_redis.get.side_effect = mock_get_side_effect
        mock_redis.delete.return_value = True

        result = await self.service.cleanup_old_jobs(days=365)

        assert result >= 1  # At least the old job should be cleaned up

    @patch('app.services.background_service.redis_client')
    def test_get_queue_stats(self, mock_redis):
        """Test getting queue statistics."""
        # Mock Redis operations
        mock_redis.client.zcard.return_value = 5  # 5 pending jobs
        mock_redis.client.keys.return_value = [
            b"background_jobs:results:job1",
            b"background_jobs:results:job2",
            b"background_jobs:results:job3"
        ]

        def mock_get_side_effect(key):
            job_data_map = {
                "background_jobs:results:job1": {"status": JobStatus.PENDING},
                "background_jobs:results:job2": {"status": JobStatus.COMPLETED},
                "background_jobs:results:job3": {"status": JobStatus.PROCESSING},
            }
            return job_data_map.get(key.decode())

        mock_redis.get.side_effect = mock_get_side_effect

        stats = self.service.get_queue_stats()

        assert 'pending' in stats
        assert 'processing' in stats
        assert 'completed' in stats
        assert 'failed' in stats
        assert stats['pending'] == 5


class TestBackgroundServiceIntegration:
    """Integration tests for BackgroundService."""

    @pytest.mark.asyncio
    @patch('app.services.background_service.redis_client')
    async def test_complete_job_lifecycle(self, mock_redis):
        """Test complete job lifecycle: enqueue -> update -> complete."""
        # Mock all Redis operations
        mock_redis.set.return_value = True
        mock_redis.client.zadd.return_value = 1
        mock_redis.client.zrangebyscore.return_value = []
        mock_redis.client.keys.return_value = []
        mock_redis.client.zcard.return_value = 0

        service = BackgroundJobService()

        # 1. Enqueue job
        job_type = "image_processing"
        job_data = {"image_id": str(uuid.uuid4()), "operations": ["resize", "optimize"]}

        job_id = await service.enqueue_job(job_type=job_type, job_data=job_data)
        assert job_id is not None

        # 2. Get initial status
        mock_redis.get.return_value = {
            'id': job_id,
            'type': job_type,
            'status': JobStatus.PENDING,
            'data': job_data
        }

        initial_status = await service.get_job_status(job_id)
        assert initial_status['status'] == JobStatus.PENDING

        # 3. Update to processing
        mock_redis.get.return_value = {
            'id': job_id,
            'type': job_type,
            'status': JobStatus.PENDING,
            'data': job_data
        }

        await service.update_job_status(job_id, JobStatus.PROCESSING)

        # 4. Complete job
        mock_redis.get.return_value = {
            'id': job_id,
            'type': job_type,
            'status': JobStatus.PROCESSING,
            'data': job_data
        }

        result = {'variants_created': 3, 'processing_time': 2.5}
        await service.update_job_status(job_id, JobStatus.COMPLETED, result=result)

        # 5. Verify final status
        mock_redis.get.return_value = {
            'id': job_id,
            'type': job_type,
            'status': JobStatus.COMPLETED,
            'data': job_data,
            'result': result
        }

        final_status = await service.get_job_status(job_id)
        assert final_status['status'] == JobStatus.COMPLETED
        assert final_status['result'] == result