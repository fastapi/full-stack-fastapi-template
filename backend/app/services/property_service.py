from typing import List, Optional
from datetime import datetime
from ...models import Property, PropertyType, PropertyStatus, User
from ...core.supabase import get_supabase_client

async def list_properties(
    property_type: Optional[PropertyType] = None,
    status: Optional[PropertyStatus] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    city: Optional[str] = None,
    bedrooms: Optional[int] = None,
    bathrooms: Optional[int] = None,
    skip: int = 0,
    limit: int = 10
) -> List[Property]:
    """
    Lista propiedades con filtros opcionales
    """
    supabase = get_supabase_client()
    query = supabase.table("properties").select("*")
    
    if property_type:
        query = query.eq("property_type", property_type)
    if status:
        query = query.eq("status", status)
    if min_price:
        query = query.gte("price", min_price)
    if max_price:
        query = query.lte("price", max_price)
    if city:
        query = query.ilike("city", f"%{city}%")
    if bedrooms:
        query = query.eq("bedrooms", bedrooms)
    if bathrooms:
        query = query.eq("bathrooms", bathrooms)
    
    query = query.range(skip, skip + limit - 1)
    response = await query.execute()
    
    return [Property(**item) for item in response.data]

async def create_property(property_data: Property, current_user: User) -> Property:
    """
    Crea una nueva propiedad
    """
    supabase = get_supabase_client()
    
    property_dict = property_data.dict()
    property_dict["owner_id"] = current_user.id
    property_dict["created_at"] = datetime.utcnow()
    property_dict["updated_at"] = datetime.utcnow()
    
    response = await supabase.table("properties").insert(property_dict).execute()
    
    if not response.data:
        raise Exception("Failed to create property")
    
    return Property(**response.data[0])

async def get_property(property_id: str) -> Optional[Property]:
    """
    Obtiene una propiedad por su ID
    """
    supabase = get_supabase_client()
    response = await supabase.table("properties").select("*").eq("id", property_id).execute()
    
    if not response.data:
        return None
    
    return Property(**response.data[0])

async def update_property(
    property_id: str,
    property_data: Property,
    current_user: User
) -> Optional[Property]:
    """
    Actualiza una propiedad existente
    """
    supabase = get_supabase_client()
    
    # Verificar que el usuario sea el propietario
    property = await get_property(property_id)
    if not property or property.owner_id != current_user.id:
        return None
    
    property_dict = property_data.dict()
    property_dict["updated_at"] = datetime.utcnow()
    
    response = await supabase.table("properties").update(property_dict).eq("id", property_id).execute()
    
    if not response.data:
        return None
    
    return Property(**response.data[0])

async def delete_property(property_id: str, current_user: User) -> bool:
    """
    Elimina una propiedad
    """
    supabase = get_supabase_client()
    
    # Verificar que el usuario sea el propietario
    property = await get_property(property_id)
    if not property or property.owner_id != current_user.id:
        return False
    
    response = await supabase.table("properties").delete().eq("id", property_id).execute()
    
    return bool(response.data)

async def search_properties(query: str, skip: int = 0, limit: int = 10) -> List[Property]:
    """
    Busca propiedades por texto
    """
    supabase = get_supabase_client()
    
    response = await supabase.table("properties").select("*").or_(
        f"title.ilike.%{query}%,description.ilike.%{query}%,address.ilike.%{query}%"
    ).range(skip, skip + limit - 1).execute()
    
    return [Property(**item) for item in response.data]

async def get_featured_properties(limit: int = 6) -> List[Property]:
    """
    Obtiene propiedades destacadas
    """
    supabase = get_supabase_client()
    
    response = await supabase.table("properties").select("*").eq("status", PropertyStatus.AVAILABLE).order("created_at", desc=True).limit(limit).execute()
    
    return [Property(**item) for item in response.data] 