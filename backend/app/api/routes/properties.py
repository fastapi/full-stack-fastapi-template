from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from ...models import Property, PropertyResponse, PropertyType, PropertyStatus
from ...core.security import get_current_user
from ...services import property_service

router = APIRouter(prefix="/properties", tags=["properties"])

@router.get("/", response_model=List[PropertyResponse])
async def list_properties(
    property_type: Optional[PropertyType] = None,
    status: Optional[PropertyStatus] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    city: Optional[str] = None,
    bedrooms: Optional[int] = None,
    bathrooms: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Lista todas las propiedades con filtros opcionales
    """
    return await property_service.list_properties(
        property_type=property_type,
        status=status,
        min_price=min_price,
        max_price=max_price,
        city=city,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        skip=skip,
        limit=limit
    )

@router.post("/", response_model=PropertyResponse)
async def create_property(
    property_data: Property,
    current_user = Depends(get_current_user)
):
    """
    Crea una nueva propiedad
    """
    return await property_service.create_property(property_data, current_user)

@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: str):
    """
    Obtiene los detalles de una propiedad específica
    """
    property = await property_service.get_property(property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    return property

@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: str,
    property_data: Property,
    current_user = Depends(get_current_user)
):
    """
    Actualiza una propiedad existente
    """
    property = await property_service.update_property(property_id, property_data, current_user)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    return property

@router.delete("/{property_id}")
async def delete_property(
    property_id: str,
    current_user = Depends(get_current_user)
):
    """
    Elimina una propiedad
    """
    success = await property_service.delete_property(property_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Property not found")
    return {"message": "Property deleted successfully"}

@router.get("/search/", response_model=List[PropertyResponse])
async def search_properties(
    query: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Busca propiedades por texto
    """
    return await property_service.search_properties(query, skip, limit)

@router.get("/featured/", response_model=List[PropertyResponse])
async def get_featured_properties(
    limit: int = Query(6, ge=1, le=20)
):
    """
    Obtiene propiedades destacadas
    """
    return await property_service.get_featured_properties(limit) 