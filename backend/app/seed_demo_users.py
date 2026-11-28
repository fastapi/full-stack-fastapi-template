import logging
import os
import sys

from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.core.db import engine
from app.core.security import verify_password
from app.models import UserCreate, UserRole, UserUpdate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEMO_USERS = {
    "demo-admin@example.com": UserRole.ADMIN,
    "demo-manager@example.com": UserRole.MANAGER,
    "demo-member@example.com": UserRole.MEMBER,
}


def seed(session: Session, password: str) -> None:
    for email, role in DEMO_USERS.items():
        user = crud.get_user_by_email(session=session, email=email)
        if user is None:
            crud.create_user(
                session=session,
                user_create=UserCreate(email=email, password=password, role=role),
            )
            logger.info("Created %s (%s)", email, role)
            continue
        update = UserUpdate()
        if user.role != role:
            update.role = role
        if not user.is_active:
            update.is_active = True
        if not verify_password(password, user.hashed_password)[0]:
            update.password = password
        if update.model_fields_set:
            crud.update_user(session=session, db_user=user, user_in=update)
            logger.info("Updated %s (%s)", email, role)
        else:
            logger.info("Unchanged %s (%s)", email, role)


def main() -> None:
    if settings.FASTAPI_ENV != "development":
        logger.error("Refusing to seed demo users unless FASTAPI_ENV=development")
        sys.exit(1)
    with Session(engine) as session:
        seed(session, os.environ.get("DEMO_USER_PASSWORD", "DemoPass123!"))


if __name__ == "__main__":
    main()
