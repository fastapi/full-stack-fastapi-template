import uuid

from sqlmodel import Session, col, func, select

from app.models import (
    Template,
    TemplateCategory,
    TemplateLanguage,
    TemplateVersion,
)


def get_template_by_id(*, session: Session, template_id: uuid.UUID) -> Template | None:
    return session.get(Template, template_id)


def list_templates(
    *,
    session: Session,
    user_id: uuid.UUID,
    is_superuser: bool,
    category: TemplateCategory | None = None,
    language: TemplateLanguage | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Template], int]:
    statement = select(Template)
    count_statement = select(func.count()).select_from(Template)

    if not is_superuser:
        statement = statement.where(Template.user_id == user_id)
        count_statement = count_statement.where(Template.user_id == user_id)

    if category:
        statement = statement.where(Template.category == category)
        count_statement = count_statement.where(Template.category == category)

    if language:
        statement = statement.where(Template.language == language)
        count_statement = count_statement.where(Template.language == language)

    if search:
        keyword = f"%{search}%"
        statement = statement.where(Template.name.ilike(keyword))
        count_statement = count_statement.where(Template.name.ilike(keyword))

    statement = (
        statement.order_by(col(Template.updated_at).desc()).offset(skip).limit(limit)
    )

    count = session.exec(count_statement).one()
    templates = list(session.exec(statement).all())
    return templates, count


def create_template(*, session: Session, template: Template) -> Template:
    session.add(template)
    session.commit()
    session.refresh(template)
    return template


def save_template(*, session: Session, template: Template) -> Template:
    session.add(template)
    session.commit()
    session.refresh(template)
    return template


def list_template_versions(
    *, session: Session, template_id: uuid.UUID
) -> list[TemplateVersion]:
    statement = (
        select(TemplateVersion)
        .where(TemplateVersion.template_id == template_id)
        .order_by(col(TemplateVersion.version).desc())
    )
    return list(session.exec(statement).all())


def get_template_version_by_id(
    *, session: Session, template_version_id: uuid.UUID
) -> TemplateVersion | None:
    return session.get(TemplateVersion, template_version_id)


def get_latest_template_version(
    *, session: Session, template_id: uuid.UUID
) -> TemplateVersion | None:
    statement = (
        select(TemplateVersion)
        .where(TemplateVersion.template_id == template_id)
        .order_by(col(TemplateVersion.version).desc())
        .limit(1)
    )
    return session.exec(statement).first()


def count_template_versions(*, session: Session, template_id: uuid.UUID) -> int:
    statement = (
        select(func.count())
        .select_from(TemplateVersion)
        .where(TemplateVersion.template_id == template_id)
    )
    return session.exec(statement).one()


def get_next_version_number(*, session: Session, template_id: uuid.UUID) -> int:
    statement = select(func.max(TemplateVersion.version)).where(
        TemplateVersion.template_id == template_id
    )
    current_max = session.exec(statement).one()
    if current_max is None:
        return 1
    return int(current_max) + 1


def create_template_version(
    *, session: Session, template_version: TemplateVersion
) -> TemplateVersion:
    session.add(template_version)
    session.commit()
    session.refresh(template_version)
    return template_version
