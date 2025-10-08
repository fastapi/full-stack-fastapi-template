from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import User, UserCreate, Organization, OrganizationCreate

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

    # Create default organization if it doesn't exist
    organization = session.exec(
        select(Organization).where(Organization.name == "Default Organization")
    ).first()
    if not organization:
        organization_in = OrganizationCreate(
            name="Default Organization",
            description="Initial organization for Mosaic"
        )
        organization = crud.create_organization(session=session, organization_in=organization_in)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)
    
    # Assign user to default organization if not already assigned
    if user and not user.organization_id:
        user.organization_id = organization.id
        session.add(user)
        session.commit()
        session.refresh(user)
