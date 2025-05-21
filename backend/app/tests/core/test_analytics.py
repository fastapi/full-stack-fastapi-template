from unittest.mock import patch, MagicMock, call
import pytest
import polars as pl
from polars.testing import assert_frame_equal
import duckdb # For duckdb.Error and spec for mock connection
import os
import logging # For checking log messages

# Functions/objects to test from the script
from backend.app.core import analytics 
from backend.app.core.analytics import get_duckdb_connection, query_duckdb, close_duckdb_connection, _DUCKDB_CONNECTION as SCRIPT_DUCKDB_CONNECTION

# Fixture to automatically mock OpenTelemetry tracer for all tests in this module
@pytest.fixture(autouse=True)
def mock_otel_tracer(monkeypatch):
    """Mocks the OpenTelemetry tracer used in analytics.py to prevent actual tracing."""
    mock_tracer_instance = MagicMock()
    mock_span = MagicMock()
    mock_tracer_instance.start_as_current_span.return_value.__enter__.return_value = mock_span
    monkeypatch.setattr(analytics, "tracer", mock_tracer_instance)

@pytest.fixture
def mock_settings_analytics(monkeypatch):
    """Mocks settings for analytics.py, specifically PARQUET_DATA_PATH."""
    mock_path = "/mocked/data/parquet"
    monkeypatch.setattr(analytics.settings, "PARQUET_DATA_PATH", mock_path)
    
    # Since USERS_PARQUET_PATH and ITEMS_PARQUET_PATH are module-level variables
    # derived from settings.PARQUET_DATA_PATH at import time, we need to update them too.
    analytics.USERS_PARQUET_PATH = os.path.join(mock_path, "users_analytics.parquet")
    analytics.ITEMS_PARQUET_PATH = os.path.join(mock_path, "items_analytics.parquet")
    
    # Yield the path for assertions if needed, though settings are directly patched
    yield {"PARQUET_DATA_PATH": mock_path}


@pytest.fixture(autouse=True) # Ensure this runs for every test to reset global state
def reset_global_duckdb_connection(monkeypatch):
    """Resets the global _DUCKDB_CONNECTION in analytics.py before and after each test."""
    # Reset before the test
    monkeypatch.setattr(analytics, "_DUCKDB_CONNECTION", None)
    yield
    # Reset after the test (optional, as next test will reset anyway, but good for cleanup)
    monkeypatch.setattr(analytics, "_DUCKDB_CONNECTION", None)


# --- Tests for get_duckdb_connection ---

def test_get_duckdb_connection_success_and_table_creation(mock_settings_analytics, monkeypatch):
    """
    Tests successful DuckDB connection and registration of Parquet files as tables.
    """
    mock_duckdb_conn_instance = MagicMock(spec=duckdb.DuckDBPyConnection)
    mock_duckdb_conn_instance.isclosed.return_value = False # Ensure it's not seen as closed if checked

    mock_duckdb_connect = MagicMock(return_value=mock_duckdb_conn_instance)
    monkeypatch.setattr(analytics.duckdb, "connect", mock_duckdb_connect)

    mock_os_path_exists = MagicMock(return_value=True) # Simulate Parquet files exist
    monkeypatch.setattr(analytics.os.path, "exists", mock_os_path_exists)

    # Call the function
    conn = get_duckdb_connection()

    # Assertions
    mock_duckdb_connect.assert_called_once_with(database=':memory:', read_only=False)
    
    expected_execute_calls = [
        call(f"CREATE OR REPLACE TABLE users AS SELECT * FROM read_parquet('{analytics.USERS_PARQUET_PATH}');"),
        call(f"CREATE OR REPLACE TABLE items AS SELECT * FROM read_parquet('{analytics.ITEMS_PARQUET_PATH}');")
    ]
    mock_duckdb_conn_instance.execute.assert_has_calls(expected_execute_calls, any_order=False)
    
    assert conn == mock_duckdb_conn_instance, "Returned connection should be the mock connection."
    # Access the global variable directly from the analytics module for assertion
    assert analytics._DUCKDB_CONNECTION == mock_duckdb_conn_instance, "Global connection variable not set."


def test_get_duckdb_connection_parquet_files_not_found(mock_settings_analytics, monkeypatch, caplog):
    """
    Tests behavior when Parquet files are not found during connection setup.
    """
    mock_duckdb_conn_instance = MagicMock(spec=duckdb.DuckDBPyConnection)
    mock_duckdb_conn_instance.isclosed.return_value = False

    mock_duckdb_connect = MagicMock(return_value=mock_duckdb_conn_instance)
    monkeypatch.setattr(analytics.duckdb, "connect", mock_duckdb_connect)

    mock_os_path_exists = MagicMock(return_value=False) # Simulate Parquet files DO NOT exist
    monkeypatch.setattr(analytics.os.path, "exists", mock_os_path_exists)
    
    # Capture logs
    caplog.set_level(logging.ERROR, logger="backend.app.core.analytics")

    # Call the function
    conn = get_duckdb_connection()

    # Assertions
    mock_duckdb_connect.assert_called_once_with(database=':memory:', read_only=False)
    
    # Check that execute was NOT called for table creation
    for exec_call in mock_duckdb_conn_instance.execute.call_args_list:
        args, _ = exec_call
        assert "CREATE OR REPLACE TABLE" not in args[0]

    # Check logs for error messages about missing files
    assert f"Users parquet file not found at {analytics.USERS_PARQUET_PATH}" in caplog.text
    assert f"Items parquet file not found at {analytics.ITEMS_PARQUET_PATH}" in caplog.text
    
    assert conn == mock_duckdb_conn_instance, "Should still return a connection object."
    assert analytics._DUCKDB_CONNECTION == mock_duckdb_conn_instance


def test_get_duckdb_connection_reuse(mock_settings_analytics, monkeypatch):
    """
    Tests that an existing connection is reused on subsequent calls.
    """
    mock_duckdb_conn_instance = MagicMock(spec=duckdb.DuckDBPyConnection)
    mock_duckdb_conn_instance.isclosed.return_value = False 

    mock_duckdb_connect = MagicMock(return_value=mock_duckdb_conn_instance)
    monkeypatch.setattr(analytics.duckdb, "connect", mock_duckdb_connect)
    
    mock_os_path_exists = MagicMock(return_value=True)
    monkeypatch.setattr(analytics.os.path, "exists", mock_os_path_exists)

    # First call - should create connection
    conn1 = get_duckdb_connection()
    mock_duckdb_connect.assert_called_once()
    assert analytics._DUCKDB_CONNECTION == mock_duckdb_conn_instance

    # Second call - should reuse existing connection
    conn2 = get_duckdb_connection()
    mock_duckdb_connect.assert_called_once() # Still called only once
    assert conn2 == conn1


# --- Tests for query_duckdb ---

def test_query_duckdb_successful(mock_settings_analytics, monkeypatch):
    """
    Tests successful query execution by query_duckdb.
    """
    mock_conn = MagicMock(spec=duckdb.DuckDBPyConnection)
    sample_df = pl.DataFrame({"id": [1, 2], "data": ["a", "b"]})
    # Mock the chain: connection.execute("query").pl()
    mock_conn.execute.return_value.pl.return_value = sample_df

    # Patch get_duckdb_connection to return our mock connection
    monkeypatch.setattr(analytics, "get_duckdb_connection", MagicMock(return_value=mock_conn))

    query_str = "SELECT * FROM users_table;"
    result_df = query_duckdb(query_str)

    analytics.get_duckdb_connection.assert_called_once()
    mock_conn.execute.assert_called_once_with(query_str)
    assert_frame_equal(result_df, sample_df)


def test_query_duckdb_execution_failure(mock_settings_analytics, monkeypatch):
    """
    Tests query execution failure handling in query_duckdb.
    """
    mock_conn = MagicMock(spec=duckdb.DuckDBPyConnection)
    # Simulate a DuckDB error on execute
    mock_conn.execute.side_effect = duckdb.Error("Simulated DuckDB query error")

    monkeypatch.setattr(analytics, "get_duckdb_connection", MagicMock(return_value=mock_conn))

    query_str = "SELECT * FROM non_existent_table;"
    
    with pytest.raises(duckdb.Error, match="Simulated DuckDB query error"):
        query_duckdb(query_str)

    analytics.get_duckdb_connection.assert_called_once()
    mock_conn.execute.assert_called_once_with(query_str)


# --- Tests for close_duckdb_connection ---

def test_close_duckdb_connection_active_connection(monkeypatch):
    """
    Tests closing an active DuckDB connection.
    """
    mock_conn_to_close = MagicMock(spec=duckdb.DuckDBPyConnection)
    mock_conn_to_close.isclosed.return_value = False
    
    # Set the global connection to our mock
    monkeypatch.setattr(analytics, "_DUCKDB_CONNECTION", mock_conn_to_close)
    
    close_duckdb_connection()

    mock_conn_to_close.close.assert_called_once()
    assert analytics._DUCKDB_CONNECTION is None, "Global connection should be reset to None."


def test_close_duckdb_connection_no_connection(monkeypatch):
    """
    Tests close_duckdb_connection when there's no active connection.
    """
    # Ensure global connection is None (which it should be due to reset_global_duckdb_connection)
    assert analytics._DUCKDB_CONNECTION is None
    
    # Call close - it should do nothing and not raise errors
    try:
        close_duckdb_connection()
    except Exception as e:
        pytest.fail(f"close_duckdb_connection raised an exception unexpectedly: {e}")


def test_close_duckdb_connection_already_closed(monkeypatch):
    """
    Tests close_duckdb_connection when the connection is already closed.
    """
    mock_conn_already_closed = MagicMock(spec=duckdb.DuckDBPyConnection)
    mock_conn_already_closed.isclosed.return_value = True # Simulate it's already closed
    
    monkeypatch.setattr(analytics, "_DUCKDB_CONNECTION", mock_conn_already_closed)
    
    close_duckdb_connection()

    # The close method on the mock connection should NOT be called if the real logic checks isclosed() first.
    # The current analytics.py code is: `if _DUCKDB_CONNECTION and not _DUCKDB_CONNECTION.isclosed():`
    # So, .close() should not be called.
    mock_conn_already_closed.close.assert_not_called()
    # _DUCKDB_CONNECTION is set to None regardless in the finally block of the original close_duckdb_connection
    # However, the span logic in the provided analytics.py means it returns if not (_DUCKDB_CONNECTION and not _DUCKDB_CONNECTION.isclosed())
    # So, if it's already closed, it does nothing, and _DUCKDB_CONNECTION is not set to None.
    # This depends on the exact implementation in analytics.py.
    # The provided analytics.py has:
    # `if not (_DUCKDB_CONNECTION and not _DUCKDB_CONNECTION.isclosed()): return`
    # This means if it's already closed, _DUCKDB_CONNECTION is NOT reset to None by close_duckdb_connection.
    # It's only reset if it *was* open and then an attempt to close it was made.
    # Let's adjust the assertion based on the provided code.
    assert analytics._DUCKDB_CONNECTION == mock_conn_already_closed, "Global connection should not be reset if already closed."
    # If the requirement is that it *should* be reset, the analytics.py code would need adjustment.
    # For this test, we test the *current* behavior.
    # The `reset_global_duckdb_connection` fixture will clean it up for the next test.
```
