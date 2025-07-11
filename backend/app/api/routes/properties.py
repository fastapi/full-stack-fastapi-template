from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, List, Dict, Any
from app.api.deps import CurrentUser, SessionDep
from app.services.property_service import PropertyService
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
    """Obtener propiedades con filtros y paginación desde PostgreSQL"""
    try:
        result = await PropertyService.get_properties(
            skip=skip,
            limit=limit,
            property_type=property_type,
            status=status,
            min_price=min_price,
            max_price=max_price,
            city=city
        )
        return result

    except Exception as e:
        logger.error(f"Error getting properties: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving properties")


@router.get("/{property_id}")
async def get_property(property_id: str, current_user: CurrentUser, session: SessionDep):
    """Obtener una propiedad específica desde PostgreSQL"""
    try:
        property_data = await PropertyService.get_property_by_id(property_id)
        
        if not property_data:
            raise HTTPException(status_code=404, detail="Property not found")
        
        return {"data": property_data}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting property {property_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving property")


@router.post("/")
async def create_property(
    property_data: Dict[str, Any] = Body(...),
    current_user: CurrentUser = None,
    session: SessionDep = None
):
    """Crear una nueva propiedad en PostgreSQL"""
    try:
        new_property = await PropertyService.create_property(property_data, current_user)
        return {"data": new_property, "message": "Property created successfully"}

    except Exception as e:
        logger.error(f"Error creating property: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error creating property: {str(e)}")


@router.patch("/{property_id}")
async def update_property(
    property_id: str,
    property_data: Dict[str, Any] = Body(...),
    current_user: CurrentUser = None,
    session: SessionDep = None
):
    """Actualizar una propiedad en PostgreSQL"""
    try:
        updated_property = await PropertyService.update_property(
            property_id, property_data, current_user
        )
        
        if not updated_property:
            raise HTTPException(
                status_code=404, 
                detail="Property not found or you don't have permission to update it"
            )
        
        return {
            "data": updated_property,
            "message": "Property updated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating property {property_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating property: {str(e)}")


@router.delete("/{property_id}")
async def delete_property(property_id: str, current_user: CurrentUser, session: SessionDep):
    """Eliminar una propiedad de PostgreSQL"""
    try:
        deleted = await PropertyService.delete_property(property_id, current_user)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Property not found or you don't have permission to delete it"
            )
        
        return {"message": f"Property {property_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting property {property_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting property: {str(e)}")


@router.get("/analytics/dashboard")
async def get_property_analytics(current_user: CurrentUser, session: SessionDep):
    """Obtener analytics reales de propiedades desde PostgreSQL"""
    try:
        analytics = await PropertyService.get_property_analytics()
        return {"data": analytics}

    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving analytics") 