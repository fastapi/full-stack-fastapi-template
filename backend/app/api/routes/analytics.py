from fastapi import APIRouter, HTTPException
import polars as pl
from typing import List
from pydantic import BaseModel

# OpenTelemetry Imports
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode # For setting span status

# Import duckdb for its specific error type
import duckdb 

from app.core.analytics import query_duckdb, PARQUET_DATA_PATH # For logging the path, if needed
import logging # For logging

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__) # Initialize OpenTelemetry Tracer

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Pydantic models for response structures
class UserItemCount(BaseModel):
    email: str
    item_count: int

class ActiveUser(BaseModel):
    user_id: int # Added user_id based on the query
    email: str
    full_name: str | None = None # Made full_name optional as it can be NULL
    item_count: int

@router.get("/items_by_user", response_model=List[UserItemCount])
def get_items_by_user():
    """
    Retrieves a list of users and the count of items they own,
    ordered by the number of items in descending order.
    Only users who own at least one item are included.
    """
    with tracer.start_as_current_span("analytics_items_by_user_handler") as span:
        query = """
        SELECT u.email, COUNT(i.item_id) AS item_count
        FROM users u
        JOIN items i ON u.user_id = i.owner_id
        GROUP BY u.email
        ORDER BY item_count DESC;
        """
        span.set_attribute("analytics.query", query)
        try:
            logger.info("Executing query for items_by_user")
            df: pl.DataFrame = query_duckdb(query) # query_duckdb is already traced
            result = df.to_dicts()
            span.set_attribute("response.items_count", len(result))
            logger.info(f"Successfully retrieved {len(result)} records for items_by_user")
            span.set_status(Status(StatusCode.OK))
            return result
        except ConnectionError as e: # Specific error from get_duckdb_connection if it fails
            logger.error(f"ConnectionError in /items_by_user: {e}. Ensure Parquet files exist at {PARQUET_DATA_PATH} and are readable.", exc_info=True)
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, f"Analytics service connection error: {e}"))
            raise HTTPException(status_code=503, detail=f"Analytics service unavailable: Database connection failed. {e}")
        except duckdb.Error as e: # Catch DuckDB specific errors
            logger.error(f"DuckDB query error in /items_by_user: {e}", exc_info=True)
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, f"Analytics query error: {e}"))
            raise HTTPException(status_code=500, detail=f"Analytics query failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in /items_by_user: {e}", exc_info=True)
            # Log the PARQUET_DATA_PATH to help diagnose if it's a file not found issue from underlying module
            logger.info(f"Current PARQUET_DATA_PATH for analytics module: {PARQUET_DATA_PATH}")
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, f"Unexpected error: {e}"))
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred while fetching items by user. {e}")

@router.get("/active_users", response_model=List[ActiveUser])
def get_active_users():
    """
    Retrieves the top 10 most active users based on the number of items they own.
    Users are ordered by item count in descending order.
    Includes users who may not own any items (LEFT JOIN).
    """
    with tracer.start_as_current_span("analytics_active_users_handler") as span:
        # Query updated to match ActiveUser model: user_id, email, full_name, item_count
        query = """
        SELECT u.user_id, u.email, u.full_name, COUNT(i.item_id) AS item_count
        FROM users u
        LEFT JOIN items i ON u.user_id = i.owner_id
        GROUP BY u.user_id, u.email, u.full_name  -- Group by all selected non-aggregated columns
        ORDER BY item_count DESC
        LIMIT 10;
        """
        span.set_attribute("analytics.query", query)
        try:
            logger.info("Executing query for active_users")
            df: pl.DataFrame = query_duckdb(query) # query_duckdb is already traced
            result = df.to_dicts()
            span.set_attribute("response.users_count", len(result))
            logger.info(f"Successfully retrieved {len(result)} records for active_users")
            span.set_status(Status(StatusCode.OK))
            return result
        except ConnectionError as e:
            logger.error(f"ConnectionError in /active_users: {e}. Ensure Parquet files exist at {PARQUET_DATA_PATH} and are readable.", exc_info=True)
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, f"Analytics service connection error: {e}"))
            raise HTTPException(status_code=503, detail=f"Analytics service unavailable: Database connection failed. {e}")
        except duckdb.Error as e: # Catch DuckDB specific errors
            logger.error(f"DuckDB query error in /active_users: {e}", exc_info=True)
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, f"Analytics query error: {e}"))
            raise HTTPException(status_code=500, detail=f"Analytics query failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in /active_users: {e}", exc_info=True)
            logger.info(f"Current PARQUET_DATA_PATH for analytics module: {PARQUET_DATA_PATH}")
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, f"Unexpected error: {e}"))
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred while fetching active users. {e}")
