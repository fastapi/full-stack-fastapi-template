import duckdb
import polars as pl
import os
import logging
from app.core.config import settings

# OpenTelemetry Imports
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s') # BasicConfig is often called by main app
logger = logging.getLogger(__name__) # Use module-level logger

# Initialize OpenTelemetry Tracer
tracer = trace.get_tracer(__name__)

# Get PARQUET_DATA_PATH from settings, with a default if not set.
# This assumes that if run, it's from the project root, or PARQUET_DATA_PATH will be an absolute path.
DEFAULT_PARQUET_PATH = os.path.join("backend", "data", "parquet")
PARQUET_DATA_PATH = getattr(settings, "PARQUET_DATA_PATH", DEFAULT_PARQUET_PATH)

USERS_PARQUET_PATH = os.path.join(PARQUET_DATA_PATH, "users_analytics.parquet")
ITEMS_PARQUET_PATH = os.path.join(PARQUET_DATA_PATH, "items_analytics.parquet")

# Global DuckDB connection instance
_DUCKDB_CONNECTION: duckdb.DuckDBPyConnection | None = None

def get_duckdb_connection() -> duckdb.DuckDBPyConnection:
    """
    Establishes and returns a DuckDB connection.
    If a connection doesn't exist or is closed, it creates a new one.
    It also registers Parquet files as tables in DuckDB.
    """
    global _DUCKDB_CONNECTION
    
    # Check if the connection is None or has been closed
    # This initial check is outside the span, as the span is for the actual connection/setup attempt.
    if _DUCKDB_CONNECTION is not None and not _DUCKDB_CONNECTION.isclosed():
        return _DUCKDB_CONNECTION

    with tracer.start_as_current_span("get_duckdb_connection_and_setup_tables") as span:
        span.set_attribute("parquet.users.path", USERS_PARQUET_PATH)
        span.set_attribute("parquet.items.path", ITEMS_PARQUET_PATH)
        users_table_created = False
        items_table_created = False
        
        try:
            logger.info("Attempting to establish a new DuckDB connection and setup tables.")
            _DUCKDB_CONNECTION = duckdb.connect(database=':memory:', read_only=False)
            logger.info("Successfully connected to DuckDB (in-memory).")
            span.set_attribute("duckdb.connection.status", "established")

            # Register users table
            if not os.path.exists(USERS_PARQUET_PATH):
                logger.error(f"Users parquet file not found at {USERS_PARQUET_PATH}. Table 'users' will not be created.")
                span.set_attribute("table.users.error", "File not found")
            else:
                logger.info(f"Found users parquet file at {USERS_PARQUET_PATH}. Creating table 'users'.")
                _DUCKDB_CONNECTION.execute(f"CREATE OR REPLACE TABLE users AS SELECT * FROM read_parquet('{USERS_PARQUET_PATH}');")
                users_table_created = True
                logger.info(f"Table 'users' created successfully from {USERS_PARQUET_PATH}.")
            span.set_attribute("table.users.created", users_table_created)

            # Register items table
            if not os.path.exists(ITEMS_PARQUET_PATH):
                logger.error(f"Items parquet file not found at {ITEMS_PARQUET_PATH}. Table 'items' will not be created.")
                span.set_attribute("table.items.error", "File not found")
            else:
                logger.info(f"Found items parquet file at {ITEMS_PARQUET_PATH}. Creating table 'items'.")
                _DUCKDB_CONNECTION.execute(f"CREATE OR REPLACE TABLE items AS SELECT * FROM read_parquet('{ITEMS_PARQUET_PATH}');")
                items_table_created = True
                logger.info(f"Table 'items' created successfully from {ITEMS_PARQUET_PATH}.")
            span.set_attribute("table.items.created", items_table_created)
            
            if not users_table_created and not items_table_created:
                 # If neither table could be created because files are missing, this might be considered an error state for the connection setup
                 # depending on strictness requirements. For now, logging handles it.
                 logger.warning("Neither users nor items table could be created due to missing Parquet files.")
                 # span.set_status(Status(StatusCode.ERROR, "Parquet files missing for table creation")) # Optional: set error if critical

            span.set_status(Status(StatusCode.OK))
            return _DUCKDB_CONNECTION
            
        except Exception as e:
            logger.error(f"Failed to connect to DuckDB or register tables: {e}", exc_info=True)
            if _DUCKDB_CONNECTION:
                _DUCKDB_CONNECTION.close()
            _DUCKDB_CONNECTION = None
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise

def query_duckdb(query: str) -> pl.DataFrame:
    """
    Executes a SQL query using DuckDB and returns the result as a Polars DataFrame.
    
    Args:
        query: The SQL query string to execute.
        
    Returns:
        A Polars DataFrame containing the query results.
        
    Raises:
        Exception: If the DuckDB connection cannot be established or if the query fails.
    """
    with tracer.start_as_current_span("duckdb_query") as span:
        span.set_attribute("db.statement", query)
        try:
            connection = get_duckdb_connection() # This will create a nested span if connection needs init
            if connection is None: # Should be handled by get_duckdb_connection raising an error
                 logger.error("Failed to get DuckDB connection for query (should have been raised by get_duckdb_connection).")
                 # This case should ideally not be reached if get_duckdb_connection is robust
                 span.set_status(Status(StatusCode.ERROR, "Failed to obtain DuckDB connection"))
                 raise ConnectionError("Failed to establish DuckDB connection.")

            logger.info(f"Executing DuckDB query: {query}")
            result_df = connection.execute(query).pl()
            logger.info(f"Query executed successfully. Result shape: {result_df.shape}")
            span.set_attribute("db.rows_returned", len(result_df))
            span.set_status(Status(StatusCode.OK))
            return result_df
        except duckdb.Error as e: # Catch DuckDB specific errors
            logger.error(f"DuckDB error executing query '{query}': {e}", exc_info=True)
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise
        except Exception as e: # Catch any other unexpected errors
            logger.error(f"An unexpected error occurred while executing DuckDB query '{query}': {e}", exc_info=True)
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise

def close_duckdb_connection():
    """
    Closes the global DuckDB connection if it's open.
    Useful for application shutdown hooks.
    """
    global _DUCKDB_CONNECTION
    if not (_DUCKDB_CONNECTION and not _DUCKDB_CONNECTION.isclosed()):
        return # Nothing to do if no connection or already closed

    with tracer.start_as_current_span("close_duckdb_connection") as span:
        try:
            _DUCKDB_CONNECTION.close()
            logger.info("DuckDB connection closed successfully.")
            span.set_status(Status(StatusCode.OK))
        except Exception as e:
            logger.error(f"Error while closing DuckDB connection: {e}", exc_info=True)
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            # Optionally re-raise if the caller needs to know about close failures
        finally:
            _DUCKDB_CONNECTION = None # Ensure it's reset

# Example usage (can be removed or kept for testing)
if __name__ == '__main__':
    logger.info("Running analytics module directly for testing.")
    
    # Create dummy Parquet files if they don't exist for testing
    # This part is for local testing of this module and might not be needed in production
    os.makedirs(PARQUET_DATA_PATH, exist_ok=True)
    if not os.path.exists(USERS_PARQUET_PATH):
        logger.info(f"Creating dummy {USERS_PARQUET_PATH} for testing.")
        pl.DataFrame({"user_id": [1, 2], "email": ["test1@example.com", "test2@example.com"]}).write_parquet(USERS_PARQUET_PATH)
    
    if not os.path.exists(ITEMS_PARQUET_PATH):
        logger.info(f"Creating dummy {ITEMS_PARQUET_PATH} for testing.")
        pl.DataFrame({"item_id": [101, 102], "owner_id": [1, 2], "title": ["Item A", "Item B"]}).write_parquet(ITEMS_PARQUET_PATH)

    try:
        # Test connection and table creation
        conn = get_duckdb_connection()
        if conn:
            logger.info("DuckDB connection obtained.")

            # Test querying users
            users_df = query_duckdb("SELECT * FROM users LIMIT 5;")
            logger.info("Users Data:")
            logger.info(f"\n{users_df}")

            # Test querying items
            items_df = query_duckdb("SELECT * FROM items LIMIT 5;")
            logger.info("Items Data:")
            logger.info(f"\n{items_df}")
            
            # Test a join query
            join_query = """
            SELECT u.email, COUNT(i.item_id) as item_count
            FROM users u
            LEFT JOIN items i ON u.user_id = i.owner_id
            GROUP BY u.email
            ORDER BY item_count DESC;
            """
            user_item_counts_df = query_duckdb(join_query)
            logger.info("User Item Counts:")
            logger.info(f"\n{user_item_counts_df}")

    except Exception as e:
        logger.error(f"An error occurred during example usage: {e}")
    finally:
        close_duckdb_connection()
        logger.info("Finished example usage and closed connection.")
