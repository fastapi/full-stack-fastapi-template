import sentry_sdk
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.auth import router as auth_router
from app.config import settings
from app.items import router as items_router
from app.private import router as private_router
from app.users import router as users_router
from app.utils import router as utils_router


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

api_router = APIRouter()
api_router.include_router(auth_router.router)
api_router.include_router(users_router.router)
api_router.include_router(utils_router.router)
api_router.include_router(items_router.router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private_router.router)

app.include_router(api_router, prefix=settings.API_V1_STR)
