"""
Email event handlers.

This module contains event handlers for email-related events.
"""
from app.core.events import event_handler
from app.core.logging import get_logger
from app.modules.email.services.email_service import EmailService
from app.modules.users.domain.events import UserCreatedEvent

# Configure logger
logger = get_logger("email_event_handlers")


def get_email_service() -> EmailService:
    """
    Get email service instance.
    
    Returns:
        EmailService instance
    """
    return EmailService()


@event_handler("user.created")
def handle_user_created_event(event: UserCreatedEvent) -> None:
    """
    Handle user created event by sending welcome email.
    
    Args:
        event: User created event
    """
    logger.info(f"Handling user.created event for user {event.user_id}")
    
    # Get email service
    email_service = get_email_service()
    
    # Send welcome email
    # Note: We don't have the actual password here, so we use a placeholder
    # The password is only known at creation time and not stored in plain text
    success = email_service.send_new_account_email(
        email_to=event.email,
        username=event.email,  # Using email as username
        password="**********"  # Password is masked in welcome email
    )
    
    if success:
        logger.info(f"Welcome email sent to {event.email}")
    else:
        logger.error(f"Failed to send welcome email to {event.email}")
