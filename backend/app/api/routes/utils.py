from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from app.api.deps import get_current_active_superuser
from app.models import Message
from app.utils import generate_test_email, send_email

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.get("/health-check/")
async def health_check() -> dict[str, bool]:
    """
    Health check endpoint including database and Redis status.
    """
    from app.api.deps import get_db
    from sqlalchemy import text
    from app.core.redis import redis_client

    # Check database connection
    db_status = False
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db_status = True
    except Exception:
        pass

    # Check Redis connection
    redis_status = redis_client.ping()

    return {
        "database": db_status,
        "redis": redis_status,
        "overall": db_status and redis_status,
    }
