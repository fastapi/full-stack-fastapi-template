import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Ticket, 
    TicketCreate, 
    TicketUpdate, 
    TicketPublic, 
    TicketsPublic, 
    TicketDetailPublic,
    Comment, 
    CommentCreate, 
    CommentPublic,
    Message,
    TicketCategory,
    TicketPriority,
    TicketStatus
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("/", response_model=TicketsPublic)
def read_tickets(
    session: SessionDep, 
    current_user: CurrentUser, 
    skip: int = 0, 
    limit: int = 100,
    page: int = Query(1, ge=1),
    category: TicketCategory = None,
    priority: TicketPriority = None,
    status: TicketStatus = None
) -> Any:
    """
    Listar todos os tickets (com filtros e paginação).
    """
    skip = (page - 1) * limit
    
    # Base query
    query = select(Ticket)
    count_query = select(func.count()).select_from(Ticket)
    
    # Apply filters
    if category:
        query = query.where(Ticket.category == category)
        count_query = count_query.where(Ticket.category == category)
    
    if priority:
        query = query.where(Ticket.priority == priority)
        count_query = count_query.where(Ticket.priority == priority)
        
    if status:
        query = query.where(Ticket.status == status)
        count_query = count_query.where(Ticket.status == status)
    
    # Apply user filter if not superuser
    if not current_user.is_superuser:
        query = query.where(Ticket.user_id == current_user.id)
        count_query = count_query.where(Ticket.user_id == current_user.id)
    
    # Get count and tickets
    count = session.exec(count_query).one()
    tickets = session.exec(query.offset(skip).limit(limit)).all()
    
    return TicketsPublic(data=tickets, count=count, page=page)


@router.get("/{id}", response_model=TicketDetailPublic)
def read_ticket(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Retorna detalhes de um ticket.
    """
    ticket = session.get(Ticket, id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    if not current_user.is_superuser and (ticket.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Permissões insuficientes")
    
    return ticket


@router.post("/", response_model=TicketPublic)
def create_ticket(
    *, session: SessionDep, current_user: CurrentUser, ticket_in: TicketCreate
) -> Any:
    """
    Criar um novo ticket.
    """
    ticket = Ticket.model_validate(ticket_in, update={"user_id": current_user.id})
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


@router.put("/{id}", response_model=TicketPublic)
def update_ticket(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    ticket_in: TicketUpdate,
) -> Any:
    """
    Atualizar um ticket existente.
    """
    ticket = session.get(Ticket, id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    if not current_user.is_superuser and (ticket.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Permissões insuficientes")
    
    update_dict = ticket_in.model_dump(exclude_unset=True)
    ticket.sqlmodel_update(update_dict)
    ticket.updated_at = func.now()  # Update the updated_at field
    
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


@router.delete("/{id}")
def delete_ticket(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Deletar um ticket.
    """
    ticket = session.get(Ticket, id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    if not current_user.is_superuser and (ticket.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Permissões insuficientes")
    
    session.delete(ticket)
    session.commit()
    return Message(message="Ticket removido com sucesso")


@router.post("/{id}/comments", response_model=CommentPublic)
def create_comment(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    comment_in: CommentCreate,
) -> Any:
    """
    Adicionar comentário a um ticket.
    """
    ticket = session.get(Ticket, id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    comment = Comment(
        **comment_in.model_dump(),
        ticket_id=id,
        user_id=current_user.id
    )
    
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment
