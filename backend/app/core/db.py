from sqlmodel import Session, create_engine, select

from app import crud
from app.core import rbac
from app.core.config import settings
from app.models import Permission, Role, User, UserCreate

engine = create_engine(str(settings.DATABASE_URL))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def _upsert_permissions(session: Session) -> dict[str, Permission]:
    permissions: dict[str, Permission] = {}
    for code in rbac.PERMISSION_CODES:
        permission = session.exec(
            select(Permission).where(Permission.code == code)
        ).first()
        if not permission:
            permission = Permission(code=code)
            session.add(permission)
            session.flush()
        permissions[code] = permission
    return permissions


def _upsert_roles(session: Session, permissions: dict[str, Permission]) -> None:
    for slug in rbac.ROLE_SLUGS:
        role = session.exec(select(Role).where(Role.slug == slug)).first()
        if not role:
            role = Role(slug=slug)
            session.add(role)
            session.flush()
        existing_codes = {permission.code for permission in role.permissions}
        for code in rbac.ROLE_PERMISSIONS[slug]:
            if code not in existing_codes:
                role.permissions.append(permissions[code])
    session.commit()


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    permissions = _upsert_permissions(session)
    _upsert_roles(session, permissions)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            role=rbac.ROLE_ADMIN,
        )
        user = crud.create_user(session=session, user_create=user_in)
