"""
🏢 GENIUS INDUSTRIES - Backend Principal
Sistema de gestión inmobiliaria con FastAPI
"""

import warnings
from pathlib import Path

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

# Importar solo módulos existentes
from .api.routes import properties, users, transactions, credits
from .core.config import settings

warnings.filterwarnings("ignore", message=".*Pydantic.*")

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}" if route.tags else route.name

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    description="API backend para Genius Industries - Sistema de gestión inmobiliaria",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers principales existentes (sin los módulos problemáticos)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(properties.router, prefix=settings.API_V1_STR)
app.include_router(transactions.router, prefix=settings.API_V1_STR)
app.include_router(credits.router, prefix=settings.API_V1_STR)

# Health check endpoint
@app.get("/")
def root():
    """
    Health check endpoint
    """
    return {
        "message": "🏢 Genius Industries Backend API",
        "status": "healthy",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    """
    Detailed health check
    """
    return {
        "status": "healthy",
        "service": "genius-industries-backend",
        "environment": settings.ENVIRONMENT,
        "database": "postgresql"
    }
