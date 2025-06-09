from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ...models import User, Ticket, Customer, Feedback
from ...services.nhost import nhost_client
from ...core.auth.roles import support_role

router = APIRouter(prefix="/support", tags=["Support"])

@router.get("/tickets")
async def get_tickets(
    status: str = None,
    current_user: User = Depends(support_role())
):
    """Obtiene los tickets de soporte"""
    try:
        query = """
            query GetTickets($status: String) {
                tickets(
                    where: {status: {_eq: $status}}
                ) {
                    id
                    title
                    description
                    status
                    priority
                    created_at
                    customer {
                        id
                        name
                        email
                    }
                    assigned_to {
                        id
                        email
                    }
                    category
                    last_updated
                }
            }
        """
        
        tickets = await nhost_client.graphql.query(
            query,
            {"status": status}
        )
        return tickets.get("data", {}).get("tickets", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tickets")
async def create_ticket(
    ticket_data: dict,
    current_user: User = Depends(support_role())
):
    """Crea un nuevo ticket de soporte"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation CreateTicket($ticket_data: jsonb!) {
                insert_tickets_one(object: $ticket_data) {
                    id
                    title
                    description
                    status
                    priority
                    customer_id
                    assigned_to
                    category
                }
            }
            """,
            {"ticket_data": ticket_data}
        )
        return result.get("data", {}).get("insert_tickets_one", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tickets/{ticket_id}")
async def update_ticket(
    ticket_id: str,
    update_data: dict,
    current_user: User = Depends(support_role())
):
    """Actualiza un ticket existente"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation UpdateTicket($id: uuid!, $update_data: jsonb!) {
                update_tickets(
                    where: {id: {_eq: $id}},
                    _set: $update_data
                ) {
                    affected_rows
                    returning {
                        id
                        status
                        last_updated
                    }
                }
            }
            """,
            {"id": ticket_id, "update_data": update_data}
        )
        return result.get("data", {}).get("update_tickets", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customers")
async def get_customers(
    current_user: User = Depends(support_role())
):
    """Obtiene la lista de clientes"""
    try:
        customers = await nhost_client.graphql.query(
            """
            query GetCustomers {
                customers {
                    id
                    name
                    email
                    phone
                    status
                    created_at
                    last_contact
                    tickets {
                        id
                        title
                        status
                    }
                }
            }
            """
        )
        return customers.get("data", {}).get("customers", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feedback")
async def get_customer_feedback(
    current_user: User = Depends(support_role())
):
    """Obtiene el feedback de los clientes"""
    try:
        feedback = await nhost_client.graphql.query(
            """
            query GetCustomerFeedback {
                customer_feedback {
                    id
                    customer {
                        id
                        name
                        email
                    }
                    rating
                    comment
                    category
                    created_at
                    status
                }
            }
            """
        )
        return feedback.get("data", {}).get("customer_feedback", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
async def create_feedback(
    feedback_data: dict,
    current_user: User = Depends(support_role())
):
    """Crea un nuevo registro de feedback"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation CreateFeedback($feedback_data: jsonb!) {
                insert_customer_feedback_one(object: $feedback_data) {
                    id
                    customer_id
                    rating
                    comment
                    category
                    created_at
                }
            }
            """,
            {"feedback_data": feedback_data}
        )
        return result.get("data", {}).get("insert_customer_feedback_one", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cases")
async def get_support_cases(
    status: str = None,
    current_user: User = Depends(support_role())
):
    """Obtiene los casos de soporte"""
    try:
        cases = await nhost_client.graphql.query(
            """
            query GetSupportCases($status: String) {
                support_cases(
                    where: {status: {_eq: $status}}
                ) {
                    id
                    title
                    description
                    status
                    priority
                    customer {
                        id
                        name
                        email
                    }
                    assigned_to {
                        id
                        email
                    }
                    created_at
                    last_updated
                    resolution
                }
            }
            """,
            {"status": status}
        )
        return cases.get("data", {}).get("support_cases", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cases")
async def create_support_case(
    case_data: dict,
    current_user: User = Depends(support_role())
):
    """Crea un nuevo caso de soporte"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation CreateSupportCase($case_data: jsonb!) {
                insert_support_cases_one(object: $case_data) {
                    id
                    title
                    description
                    status
                    priority
                    customer_id
                    assigned_to
                }
            }
            """,
            {"case_data": case_data}
        )
        return result.get("data", {}).get("insert_support_cases_one", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports")
async def get_support_reports(
    start_date: str,
    end_date: str,
    current_user: User = Depends(support_role())
):
    """Obtiene reportes de soporte"""
    try:
        reports = await nhost_client.graphql.query(
            """
            query GetSupportReports($start_date: timestamptz!, $end_date: timestamptz!) {
                support_reports(
                    where: {
                        created_at: {
                            _gte: $start_date,
                            _lte: $end_date
                        }
                    }
                ) {
                    id
                    type
                    metrics {
                        total_tickets
                        resolved_tickets
                        average_resolution_time
                        customer_satisfaction
                    }
                    period
                    created_at
                }
            }
            """,
            {"start_date": start_date, "end_date": end_date}
        )
        return reports.get("data", {}).get("support_reports", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 