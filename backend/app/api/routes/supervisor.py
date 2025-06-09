from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ...models import User, Property, Loan, Agent
from ...services.nhost import nhost_client
from ...core.auth.roles import supervisor_role

router = APIRouter(prefix="/supervisor", tags=["Supervisor"])

@router.get("/dashboard")
async def get_team_dashboard(
    current_user: User = Depends(supervisor_role())
):
    """Obtiene el dashboard del equipo con KPIs de agentes y rendimiento individual"""
    try:
        # Obtener información del equipo
        team = await nhost_client.graphql.query(
            """
            query GetTeamInfo($supervisor_id: uuid!) {
                teams(where: {supervisor_id: {_eq: $supervisor_id}}) {
                    id
                    name
                    performance_metrics {
                        total_sales
                        active_leads
                        conversion_rate
                    }
                    agents {
                        id
                        email
                        performance_metrics {
                            sales_count
                            active_leads
                            conversion_rate
                        }
                    }
                }
            }
            """,
            {"supervisor_id": current_user.id}
        )

        return team.get("data", {}).get("teams", [])[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents")
async def get_team_agents(
    current_user: User = Depends(supervisor_role())
):
    """Obtiene la lista de agentes del equipo"""
    try:
        agents = await nhost_client.graphql.query(
            """
            query GetTeamAgents($supervisor_id: uuid!) {
                users(
                    where: {
                        role: {_eq: "Agente"},
                        supervisor_id: {_eq: $supervisor_id}
                    }
                ) {
                    id
                    email
                    metadata
                    performance_metrics {
                        sales_count
                        active_leads
                        conversion_rate
                        commission_earned
                    }
                }
            }
            """,
            {"supervisor_id": current_user.id}
        )
        return agents.get("data", {}).get("users", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/{agent_id}/evaluate")
async def evaluate_agent(
    agent_id: str,
    evaluation_data: dict,
    current_user: User = Depends(supervisor_role())
):
    """Evalúa el desempeño de un agente"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation CreateAgentEvaluation(
                $agent_id: uuid!,
                $evaluation_data: jsonb!
            ) {
                insert_evaluations_one(object: {
                    user_id: $agent_id,
                    evaluator_id: $evaluator_id,
                    evaluation_data: $evaluation_data,
                    type: "agent"
                }) {
                    id
                    created_at
                }
            }
            """,
            {
                "agent_id": agent_id,
                "evaluator_id": current_user.id,
                "evaluation_data": evaluation_data
            }
        )
        return result.get("data", {}).get("insert_evaluations_one", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leads")
async def get_team_leads(
    current_user: User = Depends(supervisor_role())
):
    """Obtiene los leads del equipo"""
    try:
        leads = await nhost_client.graphql.query(
            """
            query GetTeamLeads($supervisor_id: uuid!) {
                leads(
                    where: {
                        agent: {
                            supervisor_id: {_eq: $supervisor_id}
                        }
                    }
                ) {
                    id
                    name
                    email
                    phone
                    status
                    assigned_to {
                        id
                        email
                    }
                    created_at
                    last_contact
                }
            }
            """,
            {"supervisor_id": current_user.id}
        )
        return leads.get("data", {}).get("leads", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/leads/assign")
async def assign_lead(
    lead_id: str,
    agent_id: str,
    current_user: User = Depends(supervisor_role())
):
    """Asigna un lead a un agente"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation AssignLead($lead_id: uuid!, $agent_id: uuid!) {
                update_leads(
                    where: {id: {_eq: $lead_id}},
                    _set: {assigned_to: $agent_id}
                ) {
                    affected_rows
                    returning {
                        id
                        assigned_to
                    }
                }
            }
            """,
            {"lead_id": lead_id, "agent_id": agent_id}
        )
        return result.get("data", {}).get("update_leads", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/operations")
async def get_pending_operations(
    current_user: User = Depends(supervisor_role())
):
    """Obtiene las operaciones pendientes de validación"""
    try:
        operations = await nhost_client.graphql.query(
            """
            query GetPendingOperations($supervisor_id: uuid!) {
                operations(
                    where: {
                        agent: {
                            supervisor_id: {_eq: $supervisor_id}
                        },
                        status: {_eq: "pending_validation"}
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
            {"supervisor_id": current_user.id}
        )
        return operations.get("data", {}).get("operations", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/operations/{operation_id}/validate")
async def validate_operation(
    operation_id: str,
    current_user: User = Depends(supervisor_role())
):
    """Valida una operación pendiente"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation ValidateOperation($id: uuid!, $validator_id: uuid!) {
                update_operations(
                    where: {id: {_eq: $id}},
                    _set: {
                        status: "validated",
                        validated_by: $validator_id,
                        validated_at: "now()"
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
            {"id": operation_id, "validator_id": current_user.id}
        )
        return result.get("data", {}).get("update_operations", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 