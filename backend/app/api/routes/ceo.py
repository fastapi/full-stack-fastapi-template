from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ...models import User, Property, Loan, Branch
from ...services.nhost import nhost_client
from ...core.auth.roles import ceo_role

router = APIRouter(prefix="/ceo", tags=["CEO"])

@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(ceo_role())
):
    """Obtiene el dashboard global con KPIs financieros y rendimiento de sucursales"""
    try:
        # Obtener KPIs financieros
        financial_kpis = await nhost_client.graphql.query(
            """
            query GetFinancialKPIs {
                financial_kpis {
                    total_revenue
                    total_loans
                    active_properties
                    pending_approvals
                }
            }
            """
        )

        # Obtener rendimiento de sucursales
        branch_performance = await nhost_client.graphql.query(
            """
            query GetBranchPerformance {
                branches {
                    id
                    name
                    revenue
                    active_agents
                    pending_operations
                }
            }
            """
        )

        return {
            "financial_kpis": financial_kpis.get("data", {}).get("financial_kpis", {}),
            "branch_performance": branch_performance.get("data", {}).get("branches", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users")
async def get_all_users(
    current_user: User = Depends(ceo_role())
):
    """Obtiene todos los usuarios del sistema"""
    try:
        users = await nhost_client.graphql.query(
            """
            query GetAllUsers {
                users {
                    id
                    email
                    role
                    metadata
                    created_at
                }
            }
            """
        )
        return users.get("data", {}).get("users", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    new_role: str,
    current_user: User = Depends(ceo_role())
):
    """Actualiza el rol de un usuario"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation UpdateUserRole($id: uuid!, $role: String!) {
                update_user(where: {id: {_eq: $id}}, _set: {role: $role}) {
                    affected_rows
                    returning {
                        id
                        role
                    }
                }
            }
            """,
            {"id": user_id, "role": new_role}
        )
        return result.get("data", {}).get("update_user", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/branches")
async def get_all_branches(
    current_user: User = Depends(ceo_role())
):
    """Obtiene todas las sucursales"""
    try:
        branches = await nhost_client.graphql.query(
            """
            query GetAllBranches {
                branches {
                    id
                    name
                    address
                    manager {
                        id
                        email
                    }
                    performance_metrics {
                        revenue
                        active_agents
                        pending_operations
                    }
                }
            }
            """
        )
        return branches.get("data", {}).get("branches", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/branches")
async def create_branch(
    branch: Branch,
    current_user: User = Depends(ceo_role())
):
    """Crea una nueva sucursal"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation CreateBranch($name: String!, $address: String!, $manager_id: uuid!) {
                insert_branches_one(object: {
                    name: $name,
                    address: $address,
                    manager_id: $manager_id
                }) {
                    id
                    name
                    address
                }
            }
            """,
            {
                "name": branch.name,
                "address": branch.address,
                "manager_id": branch.manager_id
            }
        )
        return result.get("data", {}).get("insert_branches_one", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-config")
async def get_system_config(
    current_user: User = Depends(ceo_role())
):
    """Obtiene la configuración global del sistema"""
    try:
        config = await nhost_client.graphql.query(
            """
            query GetSystemConfig {
                system_config {
                    id
                    key
                    value
                    description
                }
            }
            """
        )
        return config.get("data", {}).get("system_config", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/system-config")
async def update_system_config(
    key: str,
    value: str,
    current_user: User = Depends(ceo_role())
):
    """Actualiza la configuración global del sistema"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation UpdateSystemConfig($key: String!, $value: String!) {
                update_system_config(
                    where: {key: {_eq: $key}},
                    _set: {value: $value}
                ) {
                    affected_rows
                    returning {
                        key
                        value
                    }
                }
            }
            """,
            {"key": key, "value": value}
        )
        return result.get("data", {}).get("update_system_config", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 