from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, Dict, Any
from app.api.deps import CurrentUser, SessionDep
from app.services.client_service import ClientService
import logging

router = APIRouter(prefix="/clients", tags=["clients"])
logger = logging.getLogger(__name__)


@router.get("/")
async def get_clients(
    current_user: CurrentUser,
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    client_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """Obtener clientes con filtros y paginación desde PostgreSQL"""
    try:
        result = await ClientService.get_clients(
            skip=skip,
            limit=limit,
            client_type=client_type,
            status=status,
            search=search,
            agent_id=str(current_user.id)  # Solo clientes del agente actual
        )
        return result

    except Exception as e:
        logger.error(f"Error getting clients: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving clients")


@router.get("/{client_id}")
async def get_client(client_id: str, current_user: CurrentUser, session: SessionDep):
    """Obtener un cliente específico desde PostgreSQL"""
    try:
        client_data = await ClientService.get_client_by_id(client_id)
        
        if not client_data:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Verificar que el cliente pertenece al agente actual
        if client_data.get("agent_id") != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {"data": client_data}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client {client_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving client")


@router.post("/")
async def create_client(
    client_data: Dict[str, Any] = Body(...),
    current_user: CurrentUser = None,
    session: SessionDep = None
):
    """Crear un nuevo cliente en PostgreSQL"""
    try:
        # Validar campos requeridos
        required_fields = ["first_name", "last_name", "email"]
        for field in required_fields:
            if not client_data.get(field):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Field '{field}' is required"
                )
        
        new_client = await ClientService.create_client(client_data, current_user)
        return {"data": new_client, "message": "Client created successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating client: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error creating client: {str(e)}")


@router.patch("/{client_id}")
async def update_client(
    client_id: str,
    client_data: Dict[str, Any] = Body(...),
    current_user: CurrentUser = None,
    session: SessionDep = None
):
    """Actualizar un cliente en PostgreSQL"""
    try:
        updated_client = await ClientService.update_client(
            client_id, client_data, current_user
        )
        
        if not updated_client:
            raise HTTPException(
                status_code=404, 
                detail="Client not found or you don't have permission to update it"
            )
        
        return {
            "data": updated_client,
            "message": "Client updated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client {client_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating client: {str(e)}")


@router.delete("/{client_id}")
async def delete_client(client_id: str, current_user: CurrentUser, session: SessionDep):
    """Eliminar un cliente de PostgreSQL"""
    try:
        deleted = await ClientService.delete_client(client_id, current_user)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Client not found or you don't have permission to delete it"
            )
        
        return {"message": f"Client {client_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting client {client_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting client: {str(e)}")


@router.get("/analytics/dashboard")
async def get_client_analytics(current_user: CurrentUser, session: SessionDep):
    """Obtener analytics reales de clientes desde PostgreSQL"""
    try:
        analytics = await ClientService.get_client_analytics()
        return {"data": analytics}

    except Exception as e:
        logger.error(f"Error getting client analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving client analytics")


@router.get("/types/options")
async def get_client_type_options():
    """Obtener las opciones disponibles para tipos de cliente"""
    return {
        "data": [
            {"value": "buyer", "label": "Comprador"},
            {"value": "seller", "label": "Vendedor"},
            {"value": "both", "label": "Ambos"}
        ]
    }


@router.get("/status/options")
async def get_client_status_options():
    """Obtener las opciones disponibles para estados de cliente"""
    return {
        "data": [
            {"value": "active", "label": "Activo"},
            {"value": "inactive", "label": "Inactivo"}
        ]
    } 