from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import RoleEnum, User, UserCreate

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

    # Create default roles
    roles_to_create = [
        (RoleEnum.ADMIN, "System administrator with full access"),
        (RoleEnum.RUNNER, "Regular user who can register for races"),
        (RoleEnum.ORGANIZER, "Race organizer who can create and manage races"),
        (RoleEnum.VOLUNTEER, "Volunteer who can help with race operations"),
    ]

    for role_name, description in roles_to_create:
        crud.get_or_create_role(
            session=session,
            role_name=role_name.value,
            description=description
        )

    # Create first superuser
    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in, default_role=None)

        # Assign admin role to superuser
        admin_role = crud.get_role_by_name(session=session, name=RoleEnum.ADMIN.value)
        if admin_role:
            crud.assign_role_to_user(session=session, user=user, role=admin_role)
