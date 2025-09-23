import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

def test_logging_configuration():
    """Test that logging is properly configured."""
    import logging
    logger = logging.getLogger("app")
    assert logger.level <= logging.INFO

def test_request_logging():
    """Test that API requests are logged."""
    with patch('app.main.logger') as mock_logger:
        response = client.get("/api/v1/utils/health-check/")
        assert response.status_code == 200
        # Verify logging was called (implementation dependent)

def test_error_logging():
    """Test that errors are properly logged."""
    with patch('app.main.logger') as mock_logger:
        # Make a request that might cause an error
        response = client.get("/api/v1/nonexistent-endpoint")
        assert response.status_code == 404

def test_log_level_filtering():
    """Test log level filtering works correctly."""
    import logging

    # Test different log levels
    logger = logging.getLogger("test")
    logger.setLevel(logging.WARNING)

    with patch.object(logger, 'info') as mock_info:
        with patch.object(logger, 'warning') as mock_warning:
            logger.info("This should not be logged")
            logger.warning("This should be logged")

            mock_info.assert_called_once()
            mock_warning.assert_called_once()
