"""
User domain events.

This module defines events related to user operations.
"""
import uuid
from typing import Optional

from app.core.events import EventBase, publish_event


class UserCreatedEvent(EventBase):
    """
    Event emitted when a new user is created.
    
    This event is published after a user is successfully created
    and can be used by other modules to perform actions like
    sending welcome emails.
    """
    event_type: str = "user.created"
    user_id: uuid.UUID
    email: str
    full_name: Optional[str] = None
    
    def publish(self) -> None:
        """
        Publish this event to all registered handlers.
        
        This is a convenience method to make publishing events cleaner.
        """
        publish_event(self)
