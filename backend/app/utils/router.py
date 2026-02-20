from fastapi import APIRouter, Depends, status
from pydantic.networks import EmailStr

from app.auth.dependencies import get_current_active_superuser
from app.models import Message
from app.utils import service as email_service

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=status.HTTP_201_CREATED,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = email_service.generate_test_email(email_to=email_to)
    email_service.send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.get("/health-check/")
async def health_check() -> bool:
    return True
