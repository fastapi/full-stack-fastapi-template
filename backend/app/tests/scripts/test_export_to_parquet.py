import pytest
from unittest.mock import patch, MagicMock, call
import pandas as pd
import os
from sqlalchemy.exc import SQLAlchemyError # For simulating DB errors

# Functions/objects to test from the script
from backend.app.scripts.export_to_parquet import (
    main_etl_flow,
    create_output_directory,
    get_db_engine,
    export_users_data,
    export_items_data,
    setup_otel_for_script,
    run_etl_operations,
    # Import settings to allow monkeypatching its attributes if used by the script directly for config
    settings as script_settings
)

# Mock the opentelemetry trace module entirely for most tests to avoid side effects
# unless specific OTEL functionality is being tested.
@pytest.fixture(autouse=True)
def mock_otel_trace():
    with patch('backend.app.scripts.export_to_parquet.trace') as mock_trace_module:
        # Setup a mock tracer and span that can be used by the script without error
        mock_span = MagicMock()
        mock_span.get_context.return_value = MagicMock() # Mock context for Link
        mock_tracer_instance = MagicMock()
        mock_tracer_instance.start_as_current_span.return_value.__enter__.return_value = mock_span
        mock_trace_module.get_tracer.return_value = mock_tracer_instance
        mock_trace_module.get_tracer_provider.return_value.__class__.__name__ = 'ProxyTracerProvider' # Default for test_otel_setup_when_no_provider
        yield mock_trace_module

@pytest.fixture
def mock_db_engine_fixture():
    """Provides a MagicMock for the SQLAlchemy engine."""
    return MagicMock()

@pytest.fixture
def mock_pandas_fixture():
    """Provides MagicMocks for pandas operations."""
    with patch('backend.app.scripts.export_to_parquet.pd.read_sql_query') as mock_read_sql, \
         patch('backend.app.scripts.export_to_parquet.pd.DataFrame.to_parquet') as mock_to_parquet:
        yield {
            "read_sql_query": mock_read_sql,
            "to_parquet": mock_to_parquet
        }

@pytest.fixture
def mock_os_ops_fixture():
    """Provides MagicMocks for os operations."""
    with patch('backend.app.scripts.export_to_parquet.os.path.exists') as mock_exists, \
         patch('backend.app.scripts.export_to_parquet.os.makedirs') as mock_makedirs:
        yield {
            "exists": mock_exists,
            "makedirs": mock_makedirs
        }

@pytest.fixture
def test_output_dir(tmp_path):
    """Creates a temporary output directory for tests."""
    return tmp_path / "test_parquet_exports"

# This fixture will patch the settings object used by the script.
@pytest.fixture
def patched_script_settings(monkeypatch, test_output_dir):
    # Patch settings used by the script to control output path for tests
    monkeypatch.setattr(script_settings, "SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:dummy")
    monkeypatch.setattr(script_settings, "PARQUET_DATA_PATH", str(test_output_dir))
    monkeypatch.setattr(script_settings, "SERVICE_NAME", "test-service")
    return script_settings

# --- Test Cases ---

def test_successful_export(
    patched_script_settings,
    mock_db_engine_fixture, 
    mock_pandas_fixture,
    mock_os_ops_fixture,
    mock_otel_trace # Ensure OTEL is properly mocked
):
    """Test the successful export of users and items data."""
    # Arrange
    mock_os_ops_fixture["exists"].return_value = True # Assume directory exists

    sample_users_df = pd.DataFrame({'user_id': [1], 'email': ['user@example.com']})
    sample_items_df = pd.DataFrame({'item_id': [101], 'owner_id': [1]})

    def read_sql_side_effect(query_text, con):
        query_str = str(query_text).lower() # Convert query object to string
        if 'from "user"' in query_str:
            return sample_users_df
        elif 'from item' in query_str:
            return sample_items_df
        return pd.DataFrame()
    mock_pandas_fixture["read_sql_query"].side_effect = read_sql_side_effect
    
    # Patch get_db_engine to return our mock engine
    with patch('backend.app.scripts.export_to_parquet.get_db_engine', return_value=mock_db_engine_fixture):
        # Act
        main_etl_flow()

    # Assert
    # Check create_engine was called (implicitly via get_db_engine being called by main_etl_flow)
    # get_db_engine itself is patched, so we check its usage.
    # If we wanted to check create_engine inside get_db_engine, we'd need a different patch approach.

    assert mock_pandas_fixture["read_sql_query"].call_count == 2
    
    # Check to_parquet calls
    assert mock_pandas_fixture["to_parquet"].call_count == 2
    
    # Check users export
    first_call_df_arg = mock_pandas_fixture["to_parquet"].call_args_list[0][0][0]
    first_call_path_arg = mock_pandas_fixture["to_parquet"].call_args_list[0][1]
    pd.testing.assert_frame_equal(first_call_df_arg, sample_users_df)
    assert str(patched_script_settings.PARQUET_DATA_PATH / "users_analytics.parquet") == first_call_path_arg

    # Check items export
    second_call_df_arg = mock_pandas_fixture["to_parquet"].call_args_list[1][0][0]
    second_call_path_arg = mock_pandas_fixture["to_parquet"].call_args_list[1][1]
    pd.testing.assert_frame_equal(second_call_df_arg, sample_items_df)
    assert str(patched_script_settings.PARQUET_DATA_PATH / "items_analytics.parquet") == second_call_path_arg
    
    mock_os_ops_fixture["makedirs"].assert_not_called()


def test_directory_creation(
    patched_script_settings,
    mock_os_ops_fixture,
    mock_otel_trace # Ensure OTEL is properly mocked
):
    """Test that os.makedirs is called when the output directory does not exist."""
    # Arrange
    mock_os_ops_fixture["exists"].return_value = False # Simulate directory does NOT exist

    # Act
    # Call create_output_directory directly, or call main_etl_flow and check as part of it.
    # Let's test create_output_directory directly for this specific unit.
    create_output_directory()

    # Assert
    mock_os_ops_fixture["makedirs"].assert_called_once_with(str(patched_script_settings.PARQUET_DATA_PATH))

    # Test via main_etl_flow (integration check)
    mock_os_ops_fixture["exists"].return_value = False # Reset for this part
    mock_os_ops_fixture["makedirs"].reset_mock()
    
    # Mock away deeper calls to avoid full execution, focus on directory creation part of main flow
    with patch('backend.app.scripts.export_to_parquet.get_db_engine', return_value=None), \
         patch('backend.app.scripts.export_to_parquet.run_etl_operations', return_value=None):
        main_etl_flow()
    mock_os_ops_fixture["makedirs"].assert_called_once_with(str(patched_script_settings.PARQUET_DATA_PATH))


def test_db_query_failure(
    patched_script_settings,
    mock_db_engine_fixture,
    mock_pandas_fixture,
    mock_os_ops_fixture,
    caplog, # Pytest fixture to capture logs
    mock_otel_trace
):
    """Test handling of a database query failure."""
    # Arrange
    mock_os_ops_fixture["exists"].return_value = True
    mock_pandas_fixture["read_sql_query"].side_effect = SQLAlchemyError("Simulated DB query error")

    with patch('backend.app.scripts.export_to_parquet.get_db_engine', return_value=mock_db_engine_fixture):
        # Act
        # We expect main_etl_flow to catch the exception from run_etl_operations, which catches from export_...
        main_etl_flow() 

    # Assert
    # Check that read_sql_query was attempted (e.g., for users)
    mock_pandas_fixture["read_sql_query"].assert_called()
    # Check that to_parquet was not called for the failed part (or at all if it stops on first error)
    # Depending on error handling strategy (e.g., if it tries items after users fail)
    # Current script tries to export users, then items. If users query fails, items export might still be attempted.
    # The current script's export_users_data and export_items_data log errors but don't re-raise to stop run_etl_operations,
    # run_etl_operations re-raises, and main_etl_flow catches and logs.
    # Let's assume the first query (users) fails.
    mock_pandas_fixture["to_parquet"].assert_not_called() 
    
    assert "Error querying users data from DB: Simulated DB query error" in caplog.text
    # Check that the main ETL flow also logged an error
    assert "An error occurred during the main ETL flow" in caplog.text or "Error during ETL operations" in caplog.text


def test_file_writing_failure(
    patched_script_settings,
    mock_db_engine_fixture,
    mock_pandas_fixture,
    mock_os_ops_fixture,
    caplog,
    mock_otel_trace
):
    """Test handling of a Parquet file writing failure."""
    # Arrange
    mock_os_ops_fixture["exists"].return_value = True
    sample_users_df = pd.DataFrame({'user_id': [1], 'email': ['user@example.com']})
    mock_pandas_fixture["read_sql_query"].return_value = sample_users_df # Successful query
    mock_pandas_fixture["to_parquet"].side_effect = IOError("Simulated file writing error")

    with patch('backend.app.scripts.export_to_parquet.get_db_engine', return_value=mock_db_engine_fixture):
        # Act
        main_etl_flow()

    # Assert
    mock_pandas_fixture["read_sql_query"].assert_called() # Should be called at least for users
    mock_pandas_fixture["to_parquet"].assert_called() # Attempt to write users parquet
    
    assert "Error writing users data to Parquet: Simulated file writing error" in caplog.text
    assert "An error occurred during the main ETL flow" in caplog.text or "Error during ETL operations" in caplog.text


def test_otel_setup_when_provider_exists(monkeypatch, mock_otel_trace):
    """Test OTEL setup uses existing provider if one is found."""
    # Arrange
    # Simulate an existing provider being configured
    mock_otel_trace.get_tracer_provider.return_value.__class__.__name__ = 'TracerProviderSDK' # Simulate an actual SDK provider
    
    mock_set_tracer_provider = MagicMock()
    monkeypatch.setattr(mock_otel_trace, "set_tracer_provider", mock_set_tracer_provider)

    # Act
    setup_otel_for_script()

    # Assert
    # Ensure that set_tracer_provider is NOT called, as we should use the existing one.
    mock_set_tracer_provider.assert_not_called()
    # Ensure get_tracer was called to get a tracer instance from the existing provider
    mock_otel_trace.get_tracer.assert_called_with("etl-script.opentelemetry.existing_provider")


def test_otel_setup_when_no_provider(monkeypatch, mock_otel_trace, patched_script_settings):
    """Test OTEL setup creates a new provider if none exists."""
    # Arrange
    # Ensure the fixture default 'ProxyTracerProvider' is used for get_tracer_provider
    mock_otel_trace.get_tracer_provider.return_value.__class__.__name__ = 'ProxyTracerProvider'
    
    # Mock TracerProvider, SimpleSpanProcessor, ConsoleSpanExporter, Resource, set_tracer_provider
    mock_tracer_provider_class = MagicMock()
    mock_simple_span_processor_class = MagicMock()
    mock_console_span_exporter_class = MagicMock()
    mock_resource_class = MagicMock()
    mock_set_tracer_provider_func = MagicMock()

    monkeypatch.setattr('backend.app.scripts.export_to_parquet.TracerProvider', mock_tracer_provider_class)
    monkeypatch.setattr('backend.app.scripts.export_to_parquet.SimpleSpanProcessor', mock_simple_span_processor_class)
    monkeypatch.setattr('backend.app.scripts.export_to_parquet.ConsoleSpanExporter', mock_console_span_exporter_class)
    monkeypatch.setattr('backend.app.scripts.export_to_parquet.Resource', mock_resource_class)
    monkeypatch.setattr(mock_otel_trace, "set_tracer_provider", mock_set_tracer_provider_func)
    
    # Act
    setup_otel_for_script()

    # Assert
    mock_resource_class.create.assert_called_once_with({"service.name": patched_script_settings.SERVICE_NAME + "-etl-script"})
    mock_tracer_provider_class.assert_called_once()
    mock_console_span_exporter_class.assert_called_once()
    mock_simple_span_processor_class.assert_called_once()
    # Check that the processor was added to the provider
    mock_tracer_provider_instance = mock_tracer_provider_class.return_value
    mock_tracer_provider_instance.add_span_processor.assert_called_once()
    # Check that set_tracer_provider was called with the new provider
    mock_set_tracer_provider_func.assert_called_once_with(mock_tracer_provider_instance)
    # Check that get_tracer was called for the new provider
    mock_otel_trace.get_tracer.assert_called_with("etl-script.opentelemetry")

# Example of testing a specific export function if needed, though main_etl_flow covers integration
@patch('backend.app.scripts.export_to_parquet.pd.DataFrame.to_parquet')
@patch('backend.app.scripts.export_to_parquet.pd.read_sql_query')
def test_export_users_data_specific(mock_read_sql, mock_to_parquet, mock_db_engine_fixture, patched_script_settings, caplog):
    sample_df = pd.DataFrame({'user_id': [1], 'email': ['test@example.com']})
    mock_read_sql.return_value = sample_df

    export_users_data(mock_db_engine_fixture)

    mock_read_sql.assert_called_once()
    mock_to_parquet.assert_called_once_with(
        str(patched_script_settings.PARQUET_DATA_PATH / "users_analytics.parquet"),
        index=False
    )
    assert "Successfully exported users data" in caplog.text
```
