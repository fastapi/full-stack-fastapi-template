import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text
# Assuming models are accessible like this. If not, this import might need adjustment or removal if not used.
# from app.models import User, Item 
from app.core.config import settings

# OpenTelemetry Imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Status, StatusCode

# Setup Logging
# Using logging.getLogger for better module-level logging control
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

# Define Output Directory
OUTPUT_DIR = "backend/data/parquet/"

# Global tracer variable, will be initialized by setup_otel_for_script
tracer: trace.Tracer | None = None

# Define Output Directory (can be overridden by settings.PARQUET_DATA_PATH if available)
# This remains as the default if settings does not provide PARQUET_DATA_PATH
# For testing, we'll primarily mock settings or the OUTPUT_DIR itself.
DEFAULT_OUTPUT_DIR = "backend/data/parquet/"
OUTPUT_DIR = DEFAULT_OUTPUT_DIR # Initialize with default

def get_output_dir():
    """Gets the output directory, prioritizing settings if available."""
    global OUTPUT_DIR
    # In a real app, settings might be more complexly loaded, but for the script's context:
    # We assume 'settings' is available and has PARQUET_DATA_PATH.
    # The original script's analytics module used:
    # PARQUET_DATA_PATH = getattr(settings, "PARQUET_DATA_PATH", DEFAULT_PARQUET_PATH)
    # We'll adapt this for the script's OUTPUT_DIR.
    # However, the script already uses a global OUTPUT_DIR. Let's ensure it's configurable for tests.
    # For now, we'll assume tests will patch 'export_to_parquet.OUTPUT_DIR' or 'settings.PARQUET_DATA_PATH'.
    # The script itself doesn't dynamically update OUTPUT_DIR from settings post-init.
    # Let's refine this to make it more testable by having create_output_directory use a path.
    return getattr(settings, "PARQUET_DATA_PATH", DEFAULT_OUTPUT_DIR)


def create_output_directory():
    """Creates the output directory if it doesn't exist."""
    current_output_dir = get_output_dir()
    """Creates the output directory if it doesn't exist."""
    # This function could also be traced if it involved more complex operations or I/O
    if not os.path.exists(current_output_dir):
        os.makedirs(current_output_dir)
        logger.info(f"Created output directory: {current_output_dir}")

def get_db_engine():
    """Creates and returns a SQLAlchemy engine."""
    # Ensuring tracer is available if this function is called outside main context (though unlikely for this script)
    global tracer
    if not tracer: # Fallback if not initialized, though it should be by main
        tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("create_db_engine") as span:
        try:
            engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
            span.set_attribute("db.system", "postgresql") # Example attribute
            span.set_attribute("db.uri", str(settings.SQLALCHEMY_DATABASE_URI).split('@')[1] if '@' in str(settings.SQLALCHEMY_DATABASE_URI) else "uri_hidden")
            logger.info("Database engine created.")
            span.set_status(Status(StatusCode.OK))
            return engine
        except Exception as e:
            logger.error(f"Error creating database engine: {e}")
            if span:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
            raise

def export_users_data(engine):
    """Exports users data to a Parquet file."""
    global tracer
    if not tracer: tracer = trace.get_tracer(__name__)

    query = text('SELECT id AS user_id, email, is_active, is_superuser, full_name FROM "user";')
    current_output_dir = get_output_dir()
    output_path = os.path.join(current_output_dir, "users_analytics.parquet")
    
    with tracer.start_as_current_span("export_users_to_parquet") as parent_span:
        try:
            df = None
            with tracer.start_as_current_span("query_users_from_db", links=[trace.Link(parent_span.get_context())]) as query_span:
                try:
                    with engine.connect() as connection:
                        df = pd.read_sql_query(query, con=connection)
                    query_span.set_attribute("db.statement", str(query))
                    query_span.set_attribute("data.rows.queried", len(df) if df is not None else 0)
                    query_span.set_status(Status(StatusCode.OK))
                    logger.info(f"Successfully queried users data. Found {len(df) if df is not None else 0} rows.")
                except Exception as e_query:
                    logger.error(f"Error querying users data from DB: {e_query}")
                    query_span.record_exception(e_query)
                    query_span.set_status(Status(StatusCode.ERROR, str(e_query)))
                    raise # Propagate to parent span's error handling

            if df is not None: # Proceed only if data query was successful
                with tracer.start_as_current_span("write_users_to_parquet", links=[trace.Link(parent_span.get_context())]) as write_span:
                    try:
                        df.to_parquet(output_path, index=False)
                        write_span.set_attribute("parquet.file.path", output_path)
                        write_span.set_attribute("data.rows.written", len(df))
                        logger.info(f"Successfully exported users data to {output_path}")
                        write_span.set_status(Status(StatusCode.OK))
                    except Exception as e_write:
                        logger.error(f"Error writing users data to Parquet: {e_write}")
                        write_span.record_exception(e_write)
                        write_span.set_status(Status(StatusCode.ERROR, str(e_write)))
                        raise # Propagate to parent span's error handling
            
            parent_span.set_attribute("parquet.file.path", output_path)
            parent_span.set_attribute("data.rows.count", len(df) if df is not None else 0)
            parent_span.set_status(Status(StatusCode.OK))

        except Exception as e:
            logger.error(f"Error exporting users data: {e}")
            parent_span.record_exception(e)
            parent_span.set_status(Status(StatusCode.ERROR, str(e)))
            # Not re-raising here as the main loop handles logging general errors

def export_items_data(engine):
    """Exports items data to a Parquet file."""
    global tracer
    if not tracer: tracer = trace.get_tracer(__name__)

    query = text('SELECT id AS item_id, owner_id, title, description FROM item;')
    current_output_dir = get_output_dir()
    output_path = os.path.join(current_output_dir, "items_analytics.parquet")

    with tracer.start_as_current_span("export_items_to_parquet") as parent_span:
        try:
            df = None
            with tracer.start_as_current_span("query_items_from_db", links=[trace.Link(parent_span.get_context())]) as query_span:
                try:
                    with engine.connect() as connection:
                        df = pd.read_sql_query(query, con=connection)
                    query_span.set_attribute("db.statement", str(query))
                    query_span.set_attribute("data.rows.queried", len(df) if df is not None else 0)
                    query_span.set_status(Status(StatusCode.OK))
                    logger.info(f"Successfully queried items data. Found {len(df) if df is not None else 0} rows.")
                except Exception as e_query:
                    logger.error(f"Error querying items data from DB: {e_query}")
                    query_span.record_exception(e_query)
                    query_span.set_status(Status(StatusCode.ERROR, str(e_query)))
                    raise

            if df is not None:
                with tracer.start_as_current_span("write_items_to_parquet", links=[trace.Link(parent_span.get_context())]) as write_span:
                    try:
                        df.to_parquet(output_path, index=False)
                        write_span.set_attribute("parquet.file.path", output_path)
                        write_span.set_attribute("data.rows.written", len(df))
                        logger.info(f"Successfully exported items data to {output_path}")
                        write_span.set_status(Status(StatusCode.OK))
                    except Exception as e_write:
                        logger.error(f"Error writing items data to Parquet: {e_write}")
                        write_span.record_exception(e_write)
                        write_span.set_status(Status(StatusCode.ERROR, str(e_write)))
                        raise
            
            parent_span.set_attribute("parquet.file.path", output_path)
            parent_span.set_attribute("data.rows.count", len(df) if df is not None else 0)
            parent_span.set_status(Status(StatusCode.OK))

        except Exception as e:
            logger.error(f"Error exporting items data: {e}")
            parent_span.record_exception(e)
            parent_span.set_status(Status(StatusCode.ERROR, str(e)))
            # Not re-raising here

def setup_otel_for_script():
    """Configures OpenTelemetry for the script if not already configured by main app."""
    global tracer
    # Check if a global tracer provider is already set (e.g., by the main FastAPI app if script is imported)
    # This simple check might need to be more robust in complex scenarios.
    if trace.get_tracer_provider().__class__.__name__ == 'ProxyTracerProvider': # Default if no SDK provider is set
        logger.info("Configuring OpenTelemetry for script execution context.")
        resource = Resource.create({"service.name": settings.SERVICE_NAME + "-etl-script"}) # Use SERVICE_NAME from settings
        provider = TracerProvider(resource=resource)
        console_exporter = ConsoleSpanExporter() # For script output, console is fine
        processor = SimpleSpanProcessor(console_exporter)
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        tracer = trace.get_tracer("etl-script.opentelemetry") # Specific tracer name
    else:
        logger.info("OpenTelemetry already configured. Using existing provider.")
        tracer = trace.get_tracer("etl-script.opentelemetry.existing_provider")


def run_etl_operations(db_engine_instance):
    """Runs the main ETL operations: exporting users and items data."""
    # This function assumes tracer is initialized by setup_otel_for_script or already available
    global tracer
    if not tracer: # Should be initialized by setup_otel_for_script
        logger.warning("Tracer not initialized prior to run_etl_operations. OTEL setup might be missing.")
        tracer = trace.get_tracer("etl-script.opentelemetry.fallback")

    with tracer.start_as_current_span("run_etl_script_operations") as etl_ops_span:
        try:
            if db_engine_instance:
                export_users_data(db_engine_instance)
                export_items_data(db_engine_instance)
                etl_ops_span.set_status(Status(StatusCode.OK))
            else:
                logger.error("Database engine not provided to run_etl_operations.")
                etl_ops_span.set_status(Status(StatusCode.ERROR, "DB engine missing"))
        except Exception as e:
            logger.error(f"Error during ETL operations: {e}", exc_info=True)
            etl_ops_span.record_exception(e)
            etl_ops_span.set_status(Status(StatusCode.ERROR, str(e)))
            raise # Re-raise to be caught by main_etl_flow if needed

def main_etl_flow():
    """Main flow for the ETL script, including OTEL setup and cleanup."""
    setup_otel_for_script() # Initialize OpenTelemetry
    global tracer # Ensure we're using the initialized tracer

    with tracer.start_as_current_span("etl_process_to_parquet") as main_script_span:
        db_engine = None
        try:
            create_output_directory()
            db_engine = get_db_engine() # get_db_engine has its own span
            run_etl_operations(db_engine) # Core logic wrapped in its own span
            main_script_span.set_status(Status(StatusCode.OK))
        except Exception as e:
            logger.error(f"An error occurred during the main ETL flow: {e}", exc_info=True)
            main_script_span.record_exception(e)
            main_script_span.set_status(Status(StatusCode.ERROR, str(e)))
        finally:
            if db_engine:
                with tracer.start_as_current_span("dispose_db_engine_main_flow", links=[trace.Link(main_script_span.get_context())]) as dispose_span:
                    try:
                        db_engine.dispose()
                        logger.info("Database engine disposed.")
                        dispose_span.set_status(Status(StatusCode.OK))
                    except Exception as e_dispose:
                        logger.error(f"Error disposing database engine: {e_dispose}", exc_info=True)
                        dispose_span.record_exception(e_dispose)
                        dispose_span.set_status(Status(StatusCode.ERROR, str(e_dispose)))

if __name__ == "__main__":
    main_etl_flow()
