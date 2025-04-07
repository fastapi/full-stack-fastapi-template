import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.main import api_router
from app.core.config import settings
from app.core.middleware import setup_cors

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that runs before the application starts,
    and again when the application is shutting down.

    For now, just a placeholder, but we can use this to setup
    database connections, etc.
    """
    yield


app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json", lifespan=lifespan
)

# Use our custom CORS middleware instead of the default FastAPI one
setup_cors(app)

app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount the static files directory to serve static files
# app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    """
    Root endpoint for health checks
    """
    return {"message": "Hello! This is the API root. Go to /docs for API documentation."}


@app.get("/health")
def health_check():
    """
    Health check endpoint
    """
    return {"status": "ok"}
