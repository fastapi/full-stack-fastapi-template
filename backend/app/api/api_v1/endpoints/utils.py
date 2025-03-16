from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from app.api.deps import get_current_active_superuser
from app.schemas import Message, StandardResponse
from app.utils import generate_test_email, send_email

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
    response_model=StandardResponse[Message]
)
def test_email(email_to: EmailStr) -> StandardResponse[Message]:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return StandardResponse(
        data=Message(message="Test email sent"),
        message="Test email has been sent successfully"
    )


@router.get("/health-check/", response_model=StandardResponse[bool])
async def health_check() -> StandardResponse[bool]:
    """
    Endpoint for health checks and monitoring
    """
    return StandardResponse(
        data=True,
        message="API is healthy"
    ) 