from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Optional
from ...models import User, AuditLog, AuditLogResponse
from ...services.audit import AuditService
from ...core.auth.roles import ceo_role, manager_role

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/entity/{entity_type}/{entity_id}")
async def get_entity_history(
    entity_type: str,
    entity_id: str,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(manager_role())
):
    """
    Obtiene el historial de cambios de una entidad específica
    """
    try:
        logs = await AuditService.get_entity_history(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit,
            offset=offset
        )
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
async def get_user_actions(
    user_id: str,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(manager_role())
):
    """
    Obtiene el historial de acciones de un usuario específico
    """
    try:
        logs = await AuditService.get_user_actions(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_audit_logs(
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    user_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(ceo_role())
):
    """
    Busca registros de auditoría con filtros específicos
    """
    try:
        filters = {
            "entity_type": entity_type,
            "action": action,
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date
        }
        
        # Eliminar filtros None
        filters = {k: v for k, v in filters.items() if v is not None}
        
        logs = await AuditService.search_audit_logs(
            filters=filters,
            limit=limit,
            offset=offset
        )
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_audit_dashboard(
    current_user: User = Depends(ceo_role())
):
    """
    Obtiene estadísticas y resumen de la auditoría
    """
    try:
        # Obtener estadísticas generales
        stats = await nhost_client.graphql.query(
            """
            query GetAuditStats {
                audit_stats {
                    total_actions
                    actions_by_type
                    actions_by_user
                    recent_actions
                }
            }
            """
        )
        
        return stats.get("data", {}).get("audit_stats", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export")
async def export_audit_logs(
    start_date: str,
    end_date: str,
    format: str = "csv",
    current_user: User = Depends(ceo_role())
):
    """
    Exporta registros de auditoría en el formato especificado
    """
    try:
        # Obtener logs para el período especificado
        logs = await AuditService.search_audit_logs(
            filters={
                "start_date": start_date,
                "end_date": end_date
            },
            limit=1000  # Ajustar según necesidades
        )
        
        # Convertir a formato solicitado
        if format.lower() == "csv":
            # Implementar conversión a CSV
            pass
        elif format.lower() == "json":
            return logs
        else:
            raise HTTPException(
                status_code=400,
                detail="Formato no soportado. Use 'csv' o 'json'"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 