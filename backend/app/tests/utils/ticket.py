import random
import uuid
from datetime import datetime

from sqlmodel import Session

from app.models import (
    Ticket, 
    Comment, 
    User, 
    TicketCategory,
    TicketPriority,
    TicketStatus
)
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_ticket(db: Session, *, owner_id: uuid.UUID | None = None) -> Ticket:
    """
    Create a random ticket for testing
    """
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
        
    title = random_lower_string()
    description = random_lower_string()
    
    # Randomly select category, priority, and status
    category = random.choice(list(TicketCategory))
    priority = random.choice(list(TicketPriority))
    status = random.choice(list(TicketStatus))
    
    ticket = Ticket(
        title=title,
        description=description,
        category=category,
        priority=priority,
        status=status,
        user_id=owner_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def create_random_comment(
    db: Session, *, ticket_id: uuid.UUID | None = None, user_id: uuid.UUID | None = None
) -> Comment:
    """
    Create a random comment for testing
    """
    if ticket_id is None:
        ticket = create_random_ticket(db)
        ticket_id = ticket.id
        
    if user_id is None:
        user = create_random_user(db)
        user_id = user.id
    
    comment_text = random_lower_string()
    
    comment = Comment(
        comment=comment_text,
        ticket_id=ticket_id,
        user_id=user_id,
        created_at=datetime.utcnow(),
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
