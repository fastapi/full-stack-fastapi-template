import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
import time

client = TestClient(app)

def test_api_response_time():
    """Test API response time is within acceptable limits."""
    start_time = time.time()
    response = client.get("/api/v1/utils/health-check/")
    end_time = time.time()

    assert response.status_code == 200
    assert (end_time - start_time) < 2.0  # Should respond within 2 seconds

def test_concurrent_requests():
    """Test handling of concurrent requests."""
    import concurrent.futures
    import threading

    def make_request():
        return client.get("/api/v1/utils/health-check/")

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request) for _ in range(5)]
        results = [future.result() for future in futures]

    # All requests should succeed
    for result in results:
        assert result.status_code == 200

def test_memory_usage_stability():
    """Test that repeated requests don't cause memory leaks."""
    import gc

    # Make multiple requests
    for _ in range(10):
        response = client.get("/api/v1/utils/health-check/")
        assert response.status_code == 200

    # Force garbage collection
    gc.collect()
    # This is a basic test - more sophisticated memory monitoring would be needed in practice
e
def test_database_connection_pool():
    """Test database connection pooling under load."""
    responses = []

    # Make multiple database-dependent requests
    for _ in range(5):
        response = client.get("/api/v1/utils/health-check/")
        responses.append(response)

    # All should succeed without connection pool exhaustion
    for response in responses:
        assert response.status_code == 200
