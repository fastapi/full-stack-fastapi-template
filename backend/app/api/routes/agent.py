from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ...models import User, Property, Lead, Sale
from ...services.nhost import nhost_client
from ...core.auth.roles import agent_role

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.get("/properties")
async def get_my_properties(
    current_user: User = Depends(agent_role())
):
    """Obtiene las propiedades asignadas al agente"""
    try:
        properties = await nhost_client.graphql.query(
            """
            query GetAgentProperties($agent_id: uuid!) {
                properties(
                    where: {assigned_to: {_eq: $agent_id}}
                ) {
                    id
                    title
                    description
                    type
                    status
                    price
                    location
                    features
                    images
                    created_at
                    last_updated
                    visits {
                        id
                        date
                        status
                        customer {
                            id
                            name
                        }
                    }
                }
            }
            """,
            {"agent_id": current_user.id}
        )
        return properties.get("data", {}).get("properties", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/properties")
async def create_property(
    property_data: dict,
    current_user: User = Depends(agent_role())
):
    """Crea una nueva propiedad"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation CreateProperty($property_data: jsonb!) {
                insert_properties_one(object: $property_data) {
                    id
                    title
                    description
                    type
                    status
                    price
                    location
                    features
                    assigned_to
                }
            }
            """,
            {"property_data": property_data}
        )
        return result.get("data", {}).get("insert_properties_one", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leads")
async def get_my_leads(
    current_user: User = Depends(agent_role())
):
    """Obtiene los leads asignados al agente"""
    try:
        leads = await nhost_client.graphql.query(
            """
            query GetAgentLeads($agent_id: uuid!) {
                leads(
                    where: {assigned_to: {_eq: $agent_id}}
                ) {
                    id
                    name
                    email
                    phone
                    status
                    source
                    created_at
                    last_contact
                    notes
                    properties {
                        id
                        title
                        status
                    }
                }
            }
            """,
            {"agent_id": current_user.id}
        )
        return leads.get("data", {}).get("leads", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/leads")
async def create_lead(
    lead_data: dict,
    current_user: User = Depends(agent_role())
):
    """Crea un nuevo lead"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation CreateLead($lead_data: jsonb!) {
                insert_leads_one(object: $lead_data) {
                    id
                    name
                    email
                    phone
                    status
                    source
                    assigned_to
                    notes
                }
            }
            """,
            {"lead_data": lead_data}
        )
        return result.get("data", {}).get("insert_leads_one", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/visits")
async def get_my_visits(
    current_user: User = Depends(agent_role())
):
    """Obtiene las visitas programadas del agente"""
    try:
        visits = await nhost_client.graphql.query(
            """
            query GetAgentVisits($agent_id: uuid!) {
                property_visits(
                    where: {agent_id: {_eq: $agent_id}}
                ) {
                    id
                    property {
                        id
                        title
                        location
                    }
                    customer {
                        id
                        name
                        phone
                    }
                    date
                    time
                    status
                    notes
                }
            }
            """,
            {"agent_id": current_user.id}
        )
        return visits.get("data", {}).get("property_visits", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/visits")
async def schedule_visit(
    visit_data: dict,
    current_user: User = Depends(agent_role())
):
    """Programa una nueva visita"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation ScheduleVisit($visit_data: jsonb!) {
                insert_property_visits_one(object: $visit_data) {
                    id
                    property_id
                    customer_id
                    agent_id
                    date
                    time
                    status
                }
            }
            """,
            {"visit_data": visit_data}
        )
        return result.get("data", {}).get("insert_property_visits_one", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sales")
async def get_my_sales(
    current_user: User = Depends(agent_role())
):
    """Obtiene las ventas del agente"""
    try:
        sales = await nhost_client.graphql.query(
            """
            query GetAgentSales($agent_id: uuid!) {
                sales(
                    where: {agent_id: {_eq: $agent_id}}
                ) {
                    id
                    property {
                        id
                        title
                        price
                    }
                    customer {
                        id
                        name
                        email
                    }
                    amount
                    commission
                    status
                    created_at
                    closed_at
                }
            }
            """,
            {"agent_id": current_user.id}
        )
        return sales.get("data", {}).get("sales", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sales")
async def create_sale(
    sale_data: dict,
    current_user: User = Depends(agent_role())
):
    """Registra una nueva venta"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation CreateSale($sale_data: jsonb!) {
                insert_sales_one(object: $sale_data) {
                    id
                    property_id
                    customer_id
                    agent_id
                    amount
                    commission
                    status
                }
            }
            """,
            {"sale_data": sale_data}
        )
        return result.get("data", {}).get("insert_sales_one", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/commission")
async def get_commission_report(
    start_date: str,
    end_date: str,
    current_user: User = Depends(agent_role())
):
    """Obtiene el reporte de comisiones"""
    try:
        commission = await nhost_client.graphql.query(
            """
            query GetCommissionReport($agent_id: uuid!, $start_date: timestamptz!, $end_date: timestamptz!) {
                commission_reports(
                    where: {
                        agent_id: {_eq: $agent_id},
                        period: {
                            _gte: $start_date,
                            _lte: $end_date
                        }
                    }
                ) {
                    id
                    period
                    total_sales
                    total_commission
                    sales {
                        id
                        amount
                        commission
                        property {
                            title
                        }
                    }
                }
            }
            """,
            {
                "agent_id": current_user.id,
                "start_date": start_date,
                "end_date": end_date
            }
        )
        return commission.get("data", {}).get("commission_reports", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 