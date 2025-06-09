from typing import Dict, Any, Optional
from fastapi import Request
from ..models import AuditLog, AuditLogCreate
from ..services.nhost import nhost_client

class AuditService:
    @staticmethod
    async def log_action(
        user_id: str,
        action: str,
        entity_type: str,
        entity_id: str,
        changes: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """
        Registra una acción en el sistema de auditoría
        """
        try:
            # Obtener información adicional de la request si está disponible
            ip_address = None
            user_agent = None
            if request:
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")

            # Crear el registro de auditoría
            audit_log = AuditLogCreate(
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                changes=changes,
                metadata=metadata,
                ip_address=ip_address,
                user_agent=user_agent
            )

            # Guardar en la base de datos
            result = await nhost_client.graphql.mutation(
                """
                mutation CreateAuditLog($audit_log: audit_logs_insert_input!) {
                    insert_audit_logs_one(object: $audit_log) {
                        id
                        user_id
                        action
                        entity_type
                        entity_id
                        changes
                        metadata
                        created_at
                        ip_address
                        user_agent
                    }
                }
                """,
                {"audit_log": audit_log.dict()}
            )

            return AuditLog(**result["data"]["insert_audit_logs_one"])
        except Exception as e:
            print(f"Error creating audit log: {e}")
            raise

    @staticmethod
    async def get_entity_history(
        entity_type: str,
        entity_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLog]:
        """
        Obtiene el historial de cambios de una entidad
        """
        try:
            result = await nhost_client.graphql.query(
                """
                query GetEntityHistory(
                    $entity_type: String!,
                    $entity_id: String!,
                    $limit: Int!,
                    $offset: Int!
                ) {
                    audit_logs(
                        where: {
                            entity_type: {_eq: $entity_type},
                            entity_id: {_eq: $entity_id}
                        },
                        order_by: {created_at: desc},
                        limit: $limit,
                        offset: $offset
                    ) {
                        id
                        user_id
                        action
                        entity_type
                        entity_id
                        changes
                        metadata
                        created_at
                        ip_address
                        user_agent
                    }
                }
                """,
                {
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "limit": limit,
                    "offset": offset
                }
            )

            return [AuditLog(**log) for log in result["data"]["audit_logs"]]
        except Exception as e:
            print(f"Error getting entity history: {e}")
            raise

    @staticmethod
    async def get_user_actions(
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLog]:
        """
        Obtiene el historial de acciones de un usuario
        """
        try:
            result = await nhost_client.graphql.query(
                """
                query GetUserActions(
                    $user_id: String!,
                    $limit: Int!,
                    $offset: Int!
                ) {
                    audit_logs(
                        where: {user_id: {_eq: $user_id}},
                        order_by: {created_at: desc},
                        limit: $limit,
                        offset: $offset
                    ) {
                        id
                        user_id
                        action
                        entity_type
                        entity_id
                        changes
                        metadata
                        created_at
                        ip_address
                        user_agent
                    }
                }
                """,
                {
                    "user_id": user_id,
                    "limit": limit,
                    "offset": offset
                }
            )

            return [AuditLog(**log) for log in result["data"]["audit_logs"]]
        except Exception as e:
            print(f"Error getting user actions: {e}")
            raise

    @staticmethod
    async def search_audit_logs(
        filters: Dict[str, Any],
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLog]:
        """
        Busca registros de auditoría con filtros específicos
        """
        try:
            # Construir la consulta dinámicamente basada en los filtros
            where_clause = []
            variables = {
                "limit": limit,
                "offset": offset
            }

            for key, value in filters.items():
                if value is not None:
                    where_clause.append(f"{key}: {{_eq: ${key}}}")
                    variables[key] = value

            where_str = ", ".join(where_clause)
            query = f"""
                query SearchAuditLogs($limit: Int!, $offset: Int!) {{
                    audit_logs(
                        where: {{{where_str}}},
                        order_by: {{created_at: desc}},
                        limit: $limit,
                        offset: $offset
                    ) {{
                        id
                        user_id
                        action
                        entity_type
                        entity_id
                        changes
                        metadata
                        created_at
                        ip_address
                        user_agent
                    }}
                }}
            """

            result = await nhost_client.graphql.query(query, variables)
            return [AuditLog(**log) for log in result["data"]["audit_logs"]]
        except Exception as e:
            print(f"Error searching audit logs: {e}")
            raise 