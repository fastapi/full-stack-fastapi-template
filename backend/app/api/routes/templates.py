import uuid
from typing import Any, NoReturn

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    TemplateCategory,
    TemplateCreate,
    TemplateLanguage,
    TemplateListPublic,
    TemplatePublic,
    TemplatesPublic,
    TemplateUpdate,
    TemplateVersionCreate,
    TemplateVersionPublic,
    TemplateVersionsPublic,
)
from app.services import template_service
from app.services.exceptions import ServiceError

router = APIRouter(prefix="/templates", tags=["templates"])


def _raise_http_from_service_error(exc: ServiceError) -> NoReturn:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail)


def _build_template_public(session: SessionDep, template: Any) -> TemplatePublic:
    latest_version = template_service.get_template_latest_version(
        session=session, template_id=template.id
    )
    versions_count = template_service.count_template_versions(
        session=session, template_id=template.id
    )

    latest_version_public = (
        TemplateVersionPublic.model_validate(latest_version)
        if latest_version is not None
        else None
    )

    payload = template.model_dump()
    payload["versions_count"] = versions_count
    payload["latest_version"] = latest_version_public
    return TemplatePublic.model_validate(payload)


@router.get("/", response_model=TemplatesPublic)
def read_templates(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    category: TemplateCategory | None = None,
    language: TemplateLanguage | None = None,
    search: str | None = None,
) -> Any:
    templates, count = template_service.list_templates_for_user(
        session=session,
        current_user=current_user,
        category=category,
        language=language,
        search=search,
        skip=skip,
        limit=limit,
    )

    data: list[TemplateListPublic] = []
    for template in templates:
        latest_version = template_service.get_template_latest_version(
            session=session, template_id=template.id
        )
        versions_count = template_service.count_template_versions(
            session=session, template_id=template.id
        )

        payload = template.model_dump()
        payload["versions_count"] = versions_count
        payload["latest_version_number"] = (
            latest_version.version if latest_version else None
        )
        data.append(TemplateListPublic.model_validate(payload))

    return TemplatesPublic(data=data, count=count)


@router.post("/", response_model=TemplatePublic)
def create_template(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    template_in: TemplateCreate,
) -> Any:
    template = template_service.create_template_for_user(
        session=session,
        current_user=current_user,
        template_in=template_in,
    )
    return _build_template_public(session, template)


@router.get("/{template_id}", response_model=TemplatePublic)
def read_template(
    session: SessionDep, current_user: CurrentUser, template_id: uuid.UUID
) -> Any:
    try:
        template = template_service.get_template_for_user(
            session=session,
            current_user=current_user,
            template_id=template_id,
        )
    except ServiceError as exc:
        _raise_http_from_service_error(exc)

    return _build_template_public(session, template)


@router.patch("/{template_id}", response_model=TemplatePublic)
def update_template(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    template_id: uuid.UUID,
    template_in: TemplateUpdate,
) -> Any:
    try:
        template = template_service.update_template_for_user(
            session=session,
            current_user=current_user,
            template_id=template_id,
            template_in=template_in,
        )
    except ServiceError as exc:
        _raise_http_from_service_error(exc)

    return _build_template_public(session, template)


@router.get("/{template_id}/versions", response_model=TemplateVersionsPublic)
def read_template_versions(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    template_id: uuid.UUID,
) -> Any:
    try:
        versions = template_service.list_template_versions_for_user(
            session=session,
            current_user=current_user,
            template_id=template_id,
        )
    except ServiceError as exc:
        _raise_http_from_service_error(exc)

    data = [TemplateVersionPublic.model_validate(version) for version in versions]
    return TemplateVersionsPublic(data=data, count=len(data))


@router.post("/{template_id}/versions", response_model=TemplateVersionPublic)
def create_template_version(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    template_id: uuid.UUID,
    version_in: TemplateVersionCreate,
) -> Any:
    try:
        version = template_service.create_template_version_for_user(
            session=session,
            current_user=current_user,
            template_id=template_id,
            version_in=version_in,
        )
    except ServiceError as exc:
        _raise_http_from_service_error(exc)

    return TemplateVersionPublic.model_validate(version)
