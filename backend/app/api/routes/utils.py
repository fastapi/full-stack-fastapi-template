from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from app.api.deps import get_current_active_superuser
from app.models import Message
from app.utils import generate_test_email, send_email

# Create a new APIRouter instance
router = APIRouter()


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.

    This endpoint allows sending a test email to a specified address.
    It's protected and can only be accessed by active superusers.

    Args:
        email_to (EmailStr): The email address to send the test email to.

    Returns:
        Message: A message indicating that the test email was sent successfully.

    Raises:
        HTTPException: If the user is not an active superuser.

    Notes:
        This function is useful for verifying email functionality in the system.
        It generates a test email and sends it to the specified address.
    """
    # Generate test email content
    email_data = generate_test_email(email_to=email_to)

    # Send the test email
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )

    # Return a success message
    return Message(message="Test email sent")


@router.get("/health-check/")
async def health_check() -> bool:
    """
    Perform a health check.

    This endpoint returns True, indicating that the API is up and running.
    It can be used for monitoring and load balancer checks.

    Args:
        None

    Returns:
        bool: Always returns True if the API is functioning.

    Raises:
        None

    Notes:
        This is an asynchronous function that doesn't require any authentication.
        It's typically used by monitoring systems to verify the API's availability.
    """
    return True
