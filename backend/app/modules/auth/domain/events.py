"""
Auth domain events.

This module defines events related to authentication operations.
"""
from typing import Optional

from app.core.events import EventBase, publish_event


class PasswordResetRequested(EventBase):
    """
    Event emitted when a password reset is requested.
    
    This event is published after a password reset token is generated
    and can be used by other modules to perform actions like
    sending password reset emails.
    """
    event_type: str = "password.reset.requested"
    email: str
    token: str
    username: Optional[str] = None
    
    def publish(self) -> None:
        """
        Publish this event to all registered handlers.
        
        This is a convenience method to make publishing events cleaner.
        """
        publish_event(self)