from fastapi import APIRouter, Depends, HTTPException
from pydantic.networks import EmailStr
from pydantic import BaseModel

class EmailRequest(BaseModel):
    email_to: EmailStr

from app.api.deps import get_current_active_superuser
from app.models import Message
from app.utils import generate_test_email, send_email

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    status_code=200,
)
def test_email(
    email_request: EmailRequest,
    _: Depends = Depends(get_current_active_superuser),
) -> Message:
    """
    Test emails.
    """
    email_to = email_request.email_to
    
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.get("/health-check/")
async def health_check() -> bool:
    return True
