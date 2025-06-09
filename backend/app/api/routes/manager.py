from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ...models import User, Property, Loan, Branch
from ...services.nhost import nhost_client
from ...core.auth.roles import manager_role

router = APIRouter(prefix="/manager", tags=["Manager"])

@router.get("/dashboard")
async def get_branch_dashboard(
    current_user: User = Depends(manager_role())
):
    """Obtiene el dashboard de la sucursal con KPIs locales y rendimiento del equipo"""
    try:
        # Obtener información de la sucursal del gerente
        branch = await nhost_client.graphql.query(
            """
            query GetManagerBranch($manager_id: uuid!) {
                branches(where: {manager_id: {_eq: $manager_id}}) {
                    id
                    name
                    performance_metrics {
                        revenue
                        active_agents
                        pending_operations
                    }
                }
            }
            """,
            {"manager_id": current_user.id}
        )

        # Obtener KPIs del equipo
        team_kpis = await nhost_client.graphql.query(
            """
            query GetTeamKPIs($branch_id: uuid!) {
                team_kpis(where: {branch_id: {_eq: $branch_id}}) {
                    total_sales
                    active_leads
                    conversion_rate
                    average_commission
                }
            }
            """,
            {"branch_id": branch["data"]["branches"][0]["id"]}
        )

        return {
            "branch": branch.get("data", {}).get("branches", [])[0],
            "team_kpis": team_kpis.get("data", {}).get("team_kpis", [])[0]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/supervisors")
async def get_supervisors(
    current_user: User = Depends(manager_role())
):
    """Obtiene la lista de supervisores de la sucursal"""
    try:
        supervisors = await nhost_client.graphql.query(
            """
            query GetBranchSupervisors($branch_id: uuid!) {
                users(
                    where: {
                        role: {_eq: "Supervisor"},
                        branch_id: {_eq: $branch_id}
                    }
                ) {
                    id
                    email
                    metadata
                    performance_metrics {
                        team_size
                        total_sales
                        conversion_rate
                    }
                }
            }
            """,
            {"branch_id": current_user.metadata.get("branch_id")}
        )
        return supervisors.get("data", {}).get("users", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/supervisors/{supervisor_id}/evaluate")
async def evaluate_supervisor(
    supervisor_id: str,
    evaluation_data: dict,
    current_user: User = Depends(manager_role())
):
    """Evalúa el desempeño de un supervisor"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation CreateSupervisorEvaluation(
                $supervisor_id: uuid!,
                $evaluation_data: jsonb!
            ) {
                insert_evaluations_one(object: {
                    user_id: $supervisor_id,
                    evaluator_id: $evaluator_id,
                    evaluation_data: $evaluation_data,
                    type: "supervisor"
                }) {
                    id
                    created_at
                }
            }
            """,
            {
                "supervisor_id": supervisor_id,
                "evaluator_id": current_user.id,
                "evaluation_data": evaluation_data
            }
        )
        return result.get("data", {}).get("insert_evaluations_one", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending-approvals")
async def get_pending_approvals(
    current_user: User = Depends(manager_role())
):
    """Obtiene las operaciones pendientes de aprobación"""
    try:
        approvals = await nhost_client.graphql.query(
            """
            query GetPendingApprovals($branch_id: uuid!) {
                pending_approvals(
                    where: {
                        branch_id: {_eq: $branch_id},
                        status: {_eq: "pending"}
                    }
                ) {
                    id
                    type
                    amount
                    description
                    created_by {
                        id
                        email
                    }
                    created_at
                }
            }
            """,
            {"branch_id": current_user.metadata.get("branch_id")}
        )
        return approvals.get("data", {}).get("pending_approvals", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pending-approvals/{approval_id}/approve")
async def approve_operation(
    approval_id: str,
    current_user: User = Depends(manager_role())
):
    """Aprueba una operación pendiente"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation ApproveOperation($id: uuid!, $approver_id: uuid!) {
                update_pending_approvals(
                    where: {id: {_eq: $id}},
                    _set: {
                        status: "approved",
                        approved_by: $approver_id,
                        approved_at: "now()"
                    }
                ) {
                    affected_rows
                    returning {
                        id
                        status
                    }
                }
            }
            """,
            {"id": approval_id, "approver_id": current_user.id}
        )
        return result.get("data", {}).get("update_pending_approvals", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/budget")
async def get_branch_budget(
    current_user: User = Depends(manager_role())
):
    """Obtiene el presupuesto de la sucursal"""
    try:
        budget = await nhost_client.graphql.query(
            """
            query GetBranchBudget($branch_id: uuid!) {
                branch_budgets(where: {branch_id: {_eq: $branch_id}}) {
                    id
                    year
                    month
                    total_budget
                    spent_amount
                    remaining_amount
                    categories {
                        category
                        allocated
                        spent
                    }
                }
            }
            """,
            {"branch_id": current_user.metadata.get("branch_id")}
        )
        return budget.get("data", {}).get("branch_budgets", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/budget/request")
async def request_budget_adjustment(
    request_data: dict,
    current_user: User = Depends(manager_role())
):
    """Solicita un ajuste al presupuesto"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation CreateBudgetRequest(
                $branch_id: uuid!,
                $request_data: jsonb!
            ) {
                insert_budget_requests_one(object: {
                    branch_id: $branch_id,
                    requested_by: $requested_by,
                    request_data: $request_data,
                    status: "pending"
                }) {
                    id
                    created_at
                    status
                }
            }
            """,
            {
                "branch_id": current_user.metadata.get("branch_id"),
                "requested_by": current_user.id,
                "request_data": request_data
            }
        )
        return result.get("data", {}).get("insert_budget_requests_one", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 