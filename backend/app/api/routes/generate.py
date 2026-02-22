from typing import Any, NoReturn

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    ExtractVariablesRequest,
    ExtractVariablesResponse,
    RenderTemplateRequest,
    RenderTemplateResponse,
)
from app.services import generation_service
from app.services.exceptions import ServiceError

router = APIRouter(prefix="/generate", tags=["generate"])


def _raise_http_from_service_error(exc: ServiceError) -> NoReturn:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail)


@router.post("/extract", response_model=ExtractVariablesResponse)
def extract_variables(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    extract_in: ExtractVariablesRequest,
) -> Any:
    try:
        return generation_service.extract_values_for_user(
            session=session,
            current_user=current_user,
            extract_in=extract_in,
        )
    except ServiceError as exc:
        _raise_http_from_service_error(exc)


@router.post("/render", response_model=RenderTemplateResponse)
def render_template(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    render_in: RenderTemplateRequest,
) -> Any:
    try:
        return generation_service.render_for_user(
            session=session,
            current_user=current_user,
            render_in=render_in,
        )
    except ServiceError as exc:
        _raise_http_from_service_error(exc)
