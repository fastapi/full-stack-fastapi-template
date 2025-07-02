from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.api.deps import CurrentUser, SessionDep
import uuid
from datetime import datetime
import logging

router = APIRouter(prefix="/properties", tags=["properties"])
logger = logging.getLogger(__name__)


@router.get("/")
async def get_properties(
    current_user: CurrentUser,
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    property_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    city: Optional[str] = Query(None)
):
    """Obtener propiedades con filtros y paginación"""
    try:
        mock_properties = [
            {
                "id": str(uuid.uuid4()),
                "title": "Apartamento Moderno en El Poblado",
                "description": "Hermoso apartamento con vista panorámica",
                "property_type": "apartment",
                "status": "available",
                "price": 850000000,
                "currency": "COP",
                "address": "Carrera 43A #15-30",
                "city": "Medellín",
                "state": "Antioquia",
                "bedrooms": 3,
                "bathrooms": 2,
                "area": 120.0,
                "features": ["Balcón", "Aire Acondicionado"],
                "created_at": datetime.utcnow().isoformat(),
                "views": 45,
                "favorites": 12
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Casa Campestre en La Calera",
                "description": "Espectacular casa con jardín",
                "property_type": "house",
                "status": "reserved",
                "price": 1200000000,
                "currency": "COP",
                "address": "Vereda El Salitre",
                "city": "La Calera",
                "state": "Cundinamarca",
                "bedrooms": 4,
                "bathrooms": 3,
                "area": 250.0,
                "features": ["Jardín", "BBQ"],
                "created_at": datetime.utcnow().isoformat(),
                "views": 32,
                "favorites": 8
            }
        ]

        # Aplicar filtros
        filtered = mock_properties
        if property_type:
            filtered = [p for p in filtered if p["property_type"] == property_type]
        if status:
            filtered = [p for p in filtered if p["status"] == status]
        if city:
            filtered = [p for p in filtered if city.lower() in p["city"].lower()]
        if min_price:
            filtered = [p for p in filtered if p["price"] >= min_price]
        if max_price:
            filtered = [p for p in filtered if p["price"] <= max_price]

        total = len(filtered)
        properties_page = filtered[skip:skip + limit]

        return {
            "data": properties_page,
            "total": total,
            "page": (skip // limit) + 1,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }

    except Exception as e:
        logger.error(f"Error getting properties: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving properties")


@router.get("/{property_id}")
async def get_property(property_id: str, current_user: CurrentUser, session: SessionDep):
    """Obtener una propiedad específica"""
    try:
        mock_property = {
            "id": property_id,
            "title": "Apartamento Moderno en El Poblado",
            "description": "Hermoso apartamento completamente remodelado",
            "property_type": "apartment",
            "status": "available",
            "price": 850000000,
            "currency": "COP",
            "address": "Carrera 43A #15-30",
            "city": "Medellín",
            "bedrooms": 3,
            "bathrooms": 2,
            "area": 120.0,
            "features": ["Balcón", "Aire Acondicionado", "Cocina Integral"],
            "created_at": datetime.utcnow().isoformat(),
            "views": 45,
            "favorites": 12
        }

        return {"data": mock_property}

    except Exception as e:
        logger.error(f"Error getting property {property_id}: {str(e)}")
        raise HTTPException(status_code=404, detail="Property not found")


@router.post("/")
async def create_property(current_user: CurrentUser, session: SessionDep):
    """Crear una nueva propiedad"""
    try:
        new_property = {
            "id": str(uuid.uuid4()),
            "title": "Nueva Propiedad",
            "status": "available",
            "created_at": datetime.utcnow().isoformat(),
            "message": "Property created successfully"
        }
        return {"data": new_property}

    except Exception as e:
        logger.error(f"Error creating property: {str(e)}")
        raise HTTPException(status_code=400, detail="Error creating property")


@router.patch("/{property_id}")
async def update_property(property_id: str, current_user: CurrentUser, session: SessionDep):
    """Actualizar una propiedad"""
    try:
        updated_property = {
            "id": property_id,
            "message": "Property updated successfully",
            "updated_at": datetime.utcnow().isoformat()
        }
        return {"data": updated_property}

    except Exception as e:
        logger.error(f"Error updating property {property_id}: {str(e)}")
        raise HTTPException(status_code=404, detail="Property not found")


@router.delete("/{property_id}")
async def delete_property(property_id: str, current_user: CurrentUser, session: SessionDep):
    """Eliminar una propiedad"""
    try:
        return {"message": f"Property {property_id} deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting property {property_id}: {str(e)}")
        raise HTTPException(status_code=404, detail="Property not found")


@router.get("/analytics/dashboard")
async def get_property_analytics(current_user: CurrentUser, session: SessionDep):
    """Obtener analytics de propiedades"""
    try:
        analytics = {
            "total_properties": 1247,
            "available_properties": 856,
            "sold_properties": 234,
            "rented_properties": 157,
            "total_inventory_value": 45678900000,
            "average_property_price": 680000000,
            "total_sales_this_month": 12,
            "commission_earned_this_month": 125000000,
            "properties_by_city": [
                {"city": "Medellín", "count": 523, "average_price": 650000000},
                {"city": "Bogotá", "count": 412, "average_price": 780000000}
            ],
            "properties_by_type": [
                {"type": "apartment", "count": 624, "percentage": 50.04},
                {"type": "house", "count": 398, "percentage": 31.91}
            ]
        }

        return {"data": analytics}

    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving analytics") 