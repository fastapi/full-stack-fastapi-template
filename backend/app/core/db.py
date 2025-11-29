import logging

from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import OrganizationCreate, User, UserCreate

logger = logging.getLogger(__name__)

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    try:
        # Check if superuser exists
        user = session.exec(
            select(User).where(User.email == settings.FIRST_SUPERUSER)
        ).first()

        if not user:
            logger.info(f"Creating superuser: {settings.FIRST_SUPERUSER}")
            # Create the superuser's organization
            organization_in = OrganizationCreate(
                name="Admin Organization", description="Organization for admin user"
            )
            organization = crud.create_organization(
                session=session, organization_in=organization_in
            )
            logger.info(f"Created organization: {organization.name} (id: {organization.id})")

            # Create superuser and assign to their organization
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
                organization_id=organization.id,
            )
            user = crud.create_user(session=session, user_create=user_in)
            logger.info(f"Created superuser: {user.email} (id: {user.id})")
        else:
            logger.info(f"Superuser already exists: {user.email}")
    except Exception as e:
        logger.error(f"Error creating superuser: {e}", exc_info=True)
        raise
