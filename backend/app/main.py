"""
🏢 GENIUS INDUSTRIES - Backend Principal
Sistema de gestión inmobiliaria con FastAPI
"""

import warnings
from pathlib import Path

from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Configurar archivos estáticos del frontend
static_path = Path("/app/static")
if static_path.exists():
    app.mount("/assets", StaticFiles(directory=str(static_path / "assets")), name="assets")

# Health check endpoint para API
@app.get("/health")
def health_check():
    """
    Detailed health check para monitoring
    """
    return {
        "status": "healthy",
        "service": "genius-industries-backend",
        "environment": settings.ENVIRONMENT,
        "database": "postgresql"
    }

# API Root endpoint
@app.get("/api")
def api_root():
    """
    API Root endpoint
    """
    return {
        "message": "🏢 Genius Industries Backend API",
        "status": "healthy",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Frontend SPA - debe ir al final para no interferir con las rutas API
@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    """
    Servir el frontend SPA para todas las rutas que no sean API
    """
    static_file_path = static_path / full_path
    
    # Si el archivo existe, servirlo
    if static_file_path.exists() and static_file_path.is_file():
        return FileResponse(static_file_path)
    
    # Si es una ruta del frontend (SPA routing), servir index.html
    index_path = static_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    
    # Fallback
    return {"message": "Frontend not built", "note": "Build frontend and copy to /app/static"}
