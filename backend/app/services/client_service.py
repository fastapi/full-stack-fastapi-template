from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session
from fastapi import HTTPException
import uuid

from app.core.db import engine
from app.models import User

class ClientService:
    @staticmethod
    async def create_client(client_data: Dict[str, Any], current_user: User) -> Dict[str, Any]:
        """Crear un nuevo cliente en PostgreSQL"""
        try:
            with Session(engine) as session:
                client_id = str(uuid.uuid4())
                now = datetime.utcnow()
                
                # Crear tabla de clientes si no existe
                session.execute("""
                    CREATE TABLE IF NOT EXISTS clients (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        first_name VARCHAR(255) NOT NULL,
                        last_name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        phone VARCHAR(50),
                        client_type VARCHAR(50) NOT NULL DEFAULT 'buyer',
                        status VARCHAR(50) NOT NULL DEFAULT 'active',
                        notes TEXT,
                        agent_id UUID REFERENCES users(id),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Insertar cliente
                sql = """
                    INSERT INTO clients (
                        id, first_name, last_name, email, phone, client_type, 
                        status, notes, agent_id, created_at, updated_at
                    ) VALUES (
                        :id, :first_name, :last_name, :email, :phone, :client_type,
                        :status, :notes, :agent_id, :created_at, :updated_at
                    )
                    RETURNING *
                """
                
                result = session.execute(sql, {
                    "id": client_id,
                    "first_name": client_data.get("first_name", ""),
                    "last_name": client_data.get("last_name", ""),
                    "email": client_data.get("email", ""),
                    "phone": client_data.get("phone", ""),
                    "client_type": client_data.get("client_type", "buyer"),
                    "status": client_data.get("status", "active"),
                    "notes": client_data.get("notes", ""),
                    "agent_id": current_user.id,
                    "created_at": now,
                    "updated_at": now
                })
                
                session.commit()
                client_record = result.fetchone()
                
                return {
                    "id": str(client_record.id),
                    "first_name": client_record.first_name,
                    "last_name": client_record.last_name,
                    "email": client_record.email,
                    "phone": client_record.phone,
                    "client_type": client_record.client_type,
                    "status": client_record.status,
                    "notes": client_record.notes,
                    "agent_id": str(client_record.agent_id),
                    "created_at": client_record.created_at.isoformat(),
                    "updated_at": client_record.updated_at.isoformat()
                }
                
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error creating client: {str(e)}")

    @staticmethod
    async def get_clients(
        skip: int = 0,
        limit: int = 10,
        client_type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtener clientes con filtros desde PostgreSQL"""
        try:
            with Session(engine) as session:
                # Construir consulta SQL con filtros
                where_conditions = []
                params = {}
                
                if client_type:
                    where_conditions.append("client_type = :client_type")
                    params["client_type"] = client_type
                
                if status:
                    where_conditions.append("status = :status")
                    params["status"] = status
                    
                if search:
                    where_conditions.append(
                        "(LOWER(first_name) LIKE LOWER(:search) OR LOWER(last_name) LIKE LOWER(:search) OR LOWER(email) LIKE LOWER(:search))"
                    )
                    params["search"] = f"%{search}%"
                    
                if agent_id:
                    where_conditions.append("agent_id = :agent_id")
                    params["agent_id"] = agent_id
                
                where_clause = ""
                if where_conditions:
                    where_clause = "WHERE " + " AND ".join(where_conditions)
                
                # Consulta para contar total
                count_sql = f"SELECT COUNT(*) as total FROM clients {where_clause}"
                count_result = session.execute(count_sql, params).fetchone()
                total = count_result.total if count_result else 0
                
                # Consulta para obtener clientes paginados
                sql = f"""
                    SELECT * FROM clients 
                    {where_clause}
                    ORDER BY created_at DESC 
                    OFFSET :skip LIMIT :limit
                """
                params["skip"] = skip
                params["limit"] = limit
                
                result = session.execute(sql, params)
                clients = []
                
                for row in result:
                    clients.append({
                        "id": str(row.id),
                        "first_name": row.first_name,
                        "last_name": row.last_name,
                        "email": row.email,
                        "phone": row.phone,
                        "client_type": row.client_type,
                        "status": row.status,
                        "notes": row.notes,
                        "agent_id": str(row.agent_id) if row.agent_id else None,
                        "created_at": row.created_at.isoformat(),
                        "updated_at": row.updated_at.isoformat()
                    })
                
                return {
                    "data": clients,
                    "total": total,
                    "page": (skip // limit) + 1,
                    "limit": limit,
                    "total_pages": (total + limit - 1) // limit if total > 0 else 0
                }
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching clients: {str(e)}")

    @staticmethod
    async def get_client_by_id(client_id: str) -> Optional[Dict[str, Any]]:
        """Obtener un cliente específico por ID"""
        try:
            with Session(engine) as session:
                sql = "SELECT * FROM clients WHERE id = :client_id"
                result = session.execute(sql, {"client_id": client_id}).fetchone()
                
                if not result:
                    return None
                
                return {
                    "id": str(result.id),
                    "first_name": result.first_name,
                    "last_name": result.last_name,
                    "email": result.email,
                    "phone": result.phone,
                    "client_type": result.client_type,
                    "status": result.status,
                    "notes": result.notes,
                    "agent_id": str(result.agent_id) if result.agent_id else None,
                    "created_at": result.created_at.isoformat(),
                    "updated_at": result.updated_at.isoformat()
                }
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching client: {str(e)}")

    @staticmethod
    async def update_client(
        client_id: str, 
        client_data: Dict[str, Any], 
        current_user: User
    ) -> Optional[Dict[str, Any]]:
        """Actualizar un cliente existente"""
        try:
            with Session(engine) as session:
                # Verificar que el cliente existe y pertenece al agente
                check_sql = "SELECT id FROM clients WHERE id = :client_id AND agent_id = :user_id"
                check_result = session.execute(check_sql, {
                    "client_id": client_id,
                    "user_id": current_user.id
                }).fetchone()
                
                if not check_result:
                    return None
                
                # Construir UPDATE dinámico
                set_clauses = []
                params = {"client_id": client_id, "updated_at": datetime.utcnow()}
                
                for key, value in client_data.items():
                    if key not in ["id", "created_at", "updated_at", "agent_id"] and value is not None:
                        set_clauses.append(f"{key} = :{key}")
                        params[key] = value
                
                if not set_clauses:
                    return await ClientService.get_client_by_id(client_id)
                
                sql = f"""
                    UPDATE clients 
                    SET {', '.join(set_clauses)}, updated_at = :updated_at
                    WHERE id = :client_id
                    RETURNING *
                """
                
                result = session.execute(sql, params).fetchone()
                session.commit()
                
                if not result:
                    return None
                
                return {
                    "id": str(result.id),
                    "first_name": result.first_name,
                    "last_name": result.last_name,
                    "email": result.email,
                    "phone": result.phone,
                    "client_type": result.client_type,
                    "status": result.status,
                    "notes": result.notes,
                    "agent_id": str(result.agent_id) if result.agent_id else None,
                    "created_at": result.created_at.isoformat(),
                    "updated_at": result.updated_at.isoformat()
                }
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating client: {str(e)}")

    @staticmethod
    async def delete_client(client_id: str, current_user: User) -> bool:
        """Eliminar un cliente"""
        try:
            with Session(engine) as session:
                # Verificar permisos y eliminar
                sql = """
                    DELETE FROM clients 
                    WHERE id = :client_id AND agent_id = :user_id
                    RETURNING id
                """
                result = session.execute(sql, {
                    "client_id": client_id,
                    "user_id": current_user.id
                }).fetchone()
                
                session.commit()
                return result is not None
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting client: {str(e)}")

    @staticmethod
    async def get_client_analytics() -> Dict[str, Any]:
        """Obtener analytics reales de clientes desde PostgreSQL"""
        try:
            with Session(engine) as session:
                # Estadísticas básicas
                stats_sql = """
                    SELECT 
                        COUNT(*) as total_clients,
                        COUNT(CASE WHEN status = 'active' THEN 1 END) as active_clients,
                        COUNT(CASE WHEN status = 'inactive' THEN 1 END) as inactive_clients,
                        COUNT(CASE WHEN client_type = 'buyer' THEN 1 END) as buyers,
                        COUNT(CASE WHEN client_type = 'seller' THEN 1 END) as sellers,
                        COUNT(CASE WHEN client_type = 'both' THEN 1 END) as both_types
                    FROM clients
                """
                stats = session.execute(stats_sql).fetchone()
                
                # Clientes por tipo
                type_sql = """
                    SELECT 
                        client_type as type, 
                        COUNT(*) as count, 
                        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM clients), 2) as percentage
                    FROM clients
                    GROUP BY client_type
                    ORDER BY count DESC
                """
                types = session.execute(type_sql).fetchall()
                
                return {
                    "total_clients": stats.total_clients or 0,
                    "active_clients": stats.active_clients or 0,
                    "inactive_clients": stats.inactive_clients or 0,
                    "buyers": stats.buyers or 0,
                    "sellers": stats.sellers or 0,
                    "both_types": stats.both_types or 0,
                    "clients_by_type": [
                        {
                            "type": type_row.type,
                            "count": type_row.count,
                            "percentage": float(type_row.percentage or 0)
                        }
                        for type_row in types
                    ]
                }
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching client analytics: {str(e)}") 