import uuid
from typing import Any

from sqlmodel import Session

from app.models import (
    Template,
    TemplateCategory,
    TemplateCreate,
    TemplateLanguage,
    TemplateUpdate,
    TemplateVersion,
    TemplateVersionCreate,
    User,
    get_datetime_utc,
)
from app.repositories import template_repository
from app.services.exceptions import ForbiddenError, NotFoundError
from app.template_utils import normalize_variables_schema


def list_templates_for_user(
    *,
    session: Session,
    current_user: User,
    category: TemplateCategory | None = None,
    language: TemplateLanguage | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Template], int]:
    return template_repository.list_templates(
        session=session,
        user_id=current_user.id,
        is_superuser=current_user.is_superuser,
        category=category,
        language=language,
        search=search,
        skip=skip,
        limit=limit,
    )


def get_template_for_user(
    *, session: Session, current_user: User, template_id: uuid.UUID
) -> Template:
    template = template_repository.get_template_by_id(
        session=session, template_id=template_id
    )
    if template is None:
        raise NotFoundError("Template not found")
    if not current_user.is_superuser and template.user_id != current_user.id:
        raise ForbiddenError("Not enough permissions")
    return template


def create_template_for_user(
    *, session: Session, current_user: User, template_in: TemplateCreate
) -> Template:
    template = Template.model_validate(
        template_in, update={"user_id": current_user.id, "updated_at": get_datetime_utc()}
    )
    return template_repository.create_template(session=session, template=template)


def update_template_for_user(
    *,
    session: Session,
    current_user: User,
    template_id: uuid.UUID,
    template_in: TemplateUpdate,
) -> Template:
    template = get_template_for_user(
        session=session, current_user=current_user, template_id=template_id
    )
    update_data = template_in.model_dump(exclude_unset=True)
    template.sqlmodel_update(update_data)
    template.updated_at = get_datetime_utc()
    return template_repository.save_template(session=session, template=template)


def list_template_versions_for_user(
    *, session: Session, current_user: User, template_id: uuid.UUID
) -> list[TemplateVersion]:
    get_template_for_user(session=session, current_user=current_user, template_id=template_id)
    return template_repository.list_template_versions(
        session=session, template_id=template_id
    )


def get_template_version_for_user(
    *,
    session: Session,
    current_user: User,
    template_version_id: uuid.UUID,
) -> TemplateVersion:
    template_version = template_repository.get_template_version_by_id(
        session=session, template_version_id=template_version_id
    )
    if template_version is None:
        raise NotFoundError("Template version not found")
    get_template_for_user(
        session=session,
        current_user=current_user,
        template_id=template_version.template_id,
    )
    return template_version


def create_template_version_for_user(
    *,
    session: Session,
    current_user: User,
    template_id: uuid.UUID,
    version_in: TemplateVersionCreate,
) -> TemplateVersion:
    template = get_template_for_user(
        session=session, current_user=current_user, template_id=template_id
    )

    raw_schema: dict[str, Any] = {
        key: value.model_dump() if hasattr(value, "model_dump") else value
        for key, value in version_in.variables_schema.items()
    }

    normalized_schema = normalize_variables_schema(
        version_in.content,
        raw_schema,
    )

    version_number = template_repository.get_next_version_number(
        session=session,
        template_id=template.id,
    )

    template.updated_at = get_datetime_utc()
    session.add(template)

    template_version = TemplateVersion.model_validate(
        version_in,
        update={
            "template_id": template.id,
            "version": version_number,
            "created_by": current_user.id,
            "variables_schema": normalized_schema,
        },
    )
    return template_repository.create_template_version(
        session=session, template_version=template_version
    )


def get_template_latest_version(
    *, session: Session, template_id: uuid.UUID
) -> TemplateVersion | None:
    return template_repository.get_latest_template_version(
        session=session, template_id=template_id
    )


def count_template_versions(*, session: Session, template_id: uuid.UUID) -> int:
    return template_repository.count_template_versions(session=session, template_id=template_id)
