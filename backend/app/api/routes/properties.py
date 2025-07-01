from fastapi import APIRouter
from app.api.deps import CurrentUser, SessionDep

router = APIRouter(prefix="/properties", tags=["properties"])


@router.get("/")
async def get_properties(current_user: CurrentUser, session: SessionDep):
    """Obtener todas las propiedades"""
    return {
        "message": "Properties endpoint",
        "user": current_user,
        "properties": []
    }


@router.post("/")
async def create_property(current_user: CurrentUser, session: SessionDep):
    """Crear una nueva propiedad"""
    return {
        "message": "Create property - Coming soon",
        "user": current_user
    }


@router.get("/{property_id}")
async def get_property(property_id: str, current_user: CurrentUser, session: SessionDep):
    """Obtener una propiedad específica"""
    return {
        "message": f"Property {property_id} - Coming soon",
        "user": current_user,
        "property_id": property_id
    } 