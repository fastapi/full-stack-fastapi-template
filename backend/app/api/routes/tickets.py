import uuid
from typing import Any, Optional
from datetime import datetime, timedelta

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
    TicketStatus,
    PeriodType,
    User,
    TicketStatusCount,
    TicketUserCount,
    TicketUserStatusCount,
    TicketCategoryCount,
    TicketUserCategoryCount,
    TicketCategoryStatusCount,
    TicketStatusStatsResponse,
    TicketUserStatsResponse,
    TicketUserStatusStatsResponse,
    TicketCategoryStatsResponse,
    TicketUserCategoryStatsResponse,
    TicketCategoryStatusStatsResponse
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


# Função auxiliar para determinar datas de início e fim com base no tipo de período
def get_period_dates(
    period_type: PeriodType, 
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None
) -> tuple[datetime, datetime]:
    """Calcula as datas de início e fim com base no tipo de período especificado"""
    now = datetime.utcnow()
    
    if period_type == PeriodType.CUSTOM and start_date and end_date:
        return start_date, end_date
    
    if period_type == PeriodType.WEEKLY:
        # Início da semana atual (segunda-feira)
        start = now - timedelta(days=now.weekday())
        start = datetime(start.year, start.month, start.day, 0, 0, 0)
        # Fim da semana (domingo)
        end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        return start, end
        
    if period_type == PeriodType.MONTHLY:
        # Início do mês atual
        start = datetime(now.year, now.month, 1, 0, 0, 0)
        # Calcular o último dia do mês
        if now.month == 12:
            end = datetime(now.year + 1, 1, 1, 0, 0, 0) - timedelta(seconds=1)
        else:
            end = datetime(now.year, now.month + 1, 1, 0, 0, 0) - timedelta(seconds=1)
        return start, end
    
    if period_type == PeriodType.YEARLY:
        # Início do ano atual
        start = datetime(now.year, 1, 1, 0, 0, 0)
        # Fim do ano atual
        end = datetime(now.year, 12, 31, 23, 59, 59)
        return start, end
    
    # Default para CUSTOM sem datas - usar últimos 30 dias
    start = now - timedelta(days=30)
    return start, now


@router.get("/stats/status", response_model=TicketStatusStatsResponse)
def get_tickets_by_status(
    session: SessionDep,
    current_user: CurrentUser,
    period_type: PeriodType,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Any:
    """
    Obter estatísticas de tickets por status em um período específico.
    """
    start, end = get_period_dates(period_type, start_date, end_date)
    
    # Query para contar tickets por status
    query = (
        select(Ticket.status, func.count(Ticket.id).label("count"))
        .where(Ticket.created_at >= start)
        .where(Ticket.created_at <= end)
        .group_by(Ticket.status)
    )
    
    results = session.exec(query).all()
    
    # Transformar resultados no formato esperado
    data = [
        TicketStatusCount(status=status, count=count)
        for status, count in results
    ]
    
    return TicketStatusStatsResponse(
        data=data,
        period_type=period_type,
        start_date=start,
        end_date=end
    )


@router.get("/stats/users", response_model=TicketUserStatsResponse)
def get_tickets_by_user(
    session: SessionDep,
    current_user: CurrentUser,
    period_type: PeriodType,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Any:
    """
    Obter estatísticas de tickets por usuário em um período específico.
    """
    
    start, end = get_period_dates(period_type, start_date, end_date)
    
    # Query para contar tickets por usuário
    query = (
        select(User.id, User.full_name, User.email, func.count(Ticket.id).label("count"))
        .join(Ticket, User.id == Ticket.user_id)
        .where(Ticket.created_at >= start)
        .where(Ticket.created_at <= end)
        .group_by(User.id, User.full_name, User.email)
    )
    
    results = session.exec(query).all()
    
    # Transformar resultados no formato esperado
    data = [
        TicketUserCount(
            user_id=user_id,
            full_name=full_name,
            email=email,
            count=count
        )
        for user_id, full_name, email, count in results
    ]
    
    return TicketUserStatsResponse(
        data=data,
        period_type=period_type,
        start_date=start,
        end_date=end
    )


@router.get("/stats/users-status", response_model=TicketUserStatusStatsResponse)
def get_tickets_by_user_status(
    session: SessionDep,
    current_user: CurrentUser,
    period_type: PeriodType,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Any:
    """
    Obter estatísticas de tickets por usuário e status em um período específico.
    """
    
    start, end = get_period_dates(period_type, start_date, end_date)
    
    # Query para contar tickets por usuário e status
    query = (
        select(User.id, User.full_name, User.email, Ticket.status, func.count(Ticket.id).label("count"))
        .join(Ticket, User.id == Ticket.user_id)
        .where(Ticket.created_at >= start)
        .where(Ticket.created_at <= end)
        .group_by(User.id, User.full_name, User.email, Ticket.status)
    )
    
    results = session.exec(query).all()
    
    # Transformar resultados no formato esperado
    data = [
        TicketUserStatusCount(
            user_id=user_id,
            full_name=full_name,
            email=email,
            status=status,
            count=count
        )
        for user_id, full_name, email, status, count in results
    ]
    
    return TicketUserStatusStatsResponse(
        data=data,
        period_type=period_type,
        start_date=start,
        end_date=end
    )


@router.get("/stats/category", response_model=TicketCategoryStatsResponse)
def get_tickets_by_category(
    session: SessionDep,
    current_user: CurrentUser,
    period_type: PeriodType,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Any:
    """
    Obter estatísticas de tickets por categoria em um período específico.
    """
    start, end = get_period_dates(period_type, start_date, end_date)
    
    # Query para contar tickets por categoria
    query = (
        select(Ticket.category, func.count(Ticket.id).label("count"))
        .where(Ticket.created_at >= start)
        .where(Ticket.created_at <= end)
        .group_by(Ticket.category)
    )
    
    results = session.exec(query).all()
    
    # Transformar resultados no formato esperado
    data = [
        TicketCategoryCount(category=category, count=count)
        for category, count in results
    ]
    
    return TicketCategoryStatsResponse(
        data=data,
        period_type=period_type,
        start_date=start,
        end_date=end
    )


@router.get("/stats/users-category", response_model=TicketUserCategoryStatsResponse)
def get_tickets_by_user_category(
    session: SessionDep,
    current_user: CurrentUser,
    period_type: PeriodType,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Any:
    """
    Obter estatísticas de tickets por usuário e categoria em um período específico.
    """
    
    start, end = get_period_dates(period_type, start_date, end_date)
    
    # Query para contar tickets por usuário e categoria
    query = (
        select(User.id, User.full_name, User.email, Ticket.category, func.count(Ticket.id).label("count"))
        .join(Ticket, User.id == Ticket.user_id)
        .where(Ticket.created_at >= start)
        .where(Ticket.created_at <= end)
        .group_by(User.id, User.full_name, User.email, Ticket.category)
    )
    
    results = session.exec(query).all()
    
    # Transformar resultados no formato esperado
    data = [
        TicketUserCategoryCount(
            user_id=user_id,
            full_name=full_name,
            email=email,
            category=category,
            count=count
        )
        for user_id, full_name, email, category, count in results
    ]
    
    return TicketUserCategoryStatsResponse(
        data=data,
        period_type=period_type,
        start_date=start,
        end_date=end
    )


@router.get("/stats/category-status", response_model=TicketCategoryStatusStatsResponse)
def get_tickets_by_category_status(
    session: SessionDep,
    current_user: CurrentUser,
    period_type: PeriodType,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Any:
    """
    Obter estatísticas de tickets por categoria e status em um período específico.
    """
    start, end = get_period_dates(period_type, start_date, end_date)
    
    # Query para contar tickets por categoria e status
    query = (
        select(Ticket.category, Ticket.status, func.count(Ticket.id).label("count"))
        .where(Ticket.created_at >= start)
        .where(Ticket.created_at <= end)
        .group_by(Ticket.category, Ticket.status)
    )
    
    results = session.exec(query).all()
    
    # Transformar resultados no formato esperado
    data = [
        TicketCategoryStatusCount(
            category=category,
            status=status,
            count=count
        )
        for category, status, count in results
    ]
    
    return TicketCategoryStatusStatsResponse(
        data=data,
        period_type=period_type,
        start_date=start,
        end_date=end
    )


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
