from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from uuid import UUID
from ...models import Property, PropertyCreate, PropertyUpdate, PropertySearch, PropertyVisit, PropertyVisitCreate, PropertyVisitUpdate
from ...services.property import PropertyService
from ..deps import get_current_user, get_property_service
from ...models import User

router = APIRouter()

@router.post("/", response_model=Property)
async def create_property(
    property_data: PropertyCreate,
    current_user: User = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
):
    """Crear una nueva propiedad"""
    if current_user.role not in ["agent", "manager", "supervisor"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear propiedades")
    
    return await property_service.create_property(property_data)

@router.get("/{property_id}", response_model=Property)
async def get_property(
    property_id: UUID,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
):
    """Obtener una propiedad por su ID"""
    property = await property_service.get_property(property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    
    # Registrar la vista
    await property_service.record_view(
        property_id=property_id,
        user_id=current_user.id if current_user else None,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "")
    )
    
    return property

@router.put("/{property_id}", response_model=Property)
async def update_property(
    property_id: UUID,
    property_data: PropertyUpdate,
    current_user: User = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
):
    """Actualizar una propiedad"""
    if current_user.role not in ["agent", "manager", "supervisor"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar propiedades")
    
    property = await property_service.update_property(property_id, property_data)
    if not property:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    
    return property

@router.delete("/{property_id}")
async def delete_property(
    property_id: UUID,
    current_user: User = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
):
    """Eliminar una propiedad"""
    if current_user.role not in ["manager", "supervisor"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar propiedades")
    
    success = await property_service.delete_property(property_id)
    if not success:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    
    return {"message": "Propiedad eliminada exitosamente"}

@router.get("/", response_model=List[Property])
async def search_properties(
    search_params: PropertySearch = Depends(),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    property_service: PropertyService = Depends(get_property_service)
):
    """Buscar propiedades según criterios"""
    return await property_service.search_properties(search_params, limit, offset)

@router.post("/{property_id}/visits", response_model=PropertyVisit)
async def schedule_visit(
    property_id: UUID,
    visit_data: PropertyVisitCreate,
    current_user: User = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
):
    """Programar una visita a una propiedad"""
    if current_user.role not in ["agent", "client"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para programar visitas")
    
    # Verificar que la propiedad existe
    property = await property_service.get_property(property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    
    return await property_service.schedule_visit(visit_data)

@router.put("/visits/{visit_id}", response_model=PropertyVisit)
async def update_visit(
    visit_id: UUID,
    visit_data: PropertyVisitUpdate,
    current_user: User = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
):
    """Actualizar el estado de una visita"""
    if current_user.role not in ["agent", "manager", "supervisor"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar visitas")
    
    visit = await property_service.update_visit(visit_id, visit_data)
    if not visit:
        raise HTTPException(status_code=404, detail="Visita no encontrada")
    
    return visit

@router.post("/{property_id}/favorite")
async def toggle_favorite(
    property_id: UUID,
    current_user: User = Depends(get_current_user),
    property_service: PropertyService = Depends(get_property_service)
):
    """Agregar/quitar una propiedad de favoritos"""
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Solo los clientes pueden marcar propiedades como favoritas")
    
    # Verificar que la propiedad existe
    property = await property_service.get_property(property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    
    is_favorite = await property_service.toggle_favorite(property_id, current_user.id)
    return {"is_favorite": is_favorite} 