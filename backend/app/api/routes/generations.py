import uuid
from typing import Any, NoReturn

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    GenerationCreate,
    GenerationPublic,
    GenerationsPublic,
    GenerationUpdate,
)
from app.services import generation_service
from app.services.exceptions import ServiceError

router = APIRouter(prefix="/generations", tags=["generations"])


def _raise_http_from_service_error(exc: ServiceError) -> NoReturn:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail)


@router.get("/", response_model=GenerationsPublic)
def read_generations(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    generations, count = generation_service.list_generations_for_user(
        session=session,
        current_user=current_user,
        skip=skip,
        limit=limit,
    )
    data = [GenerationPublic.model_validate(generation) for generation in generations]
    return GenerationsPublic(data=data, count=count)


@router.get("/{generation_id}", response_model=GenerationPublic)
def read_generation(
    session: SessionDep, current_user: CurrentUser, generation_id: uuid.UUID
) -> Any:
    try:
        generation = generation_service.get_generation_for_user(
            session=session,
            current_user=current_user,
            generation_id=generation_id,
        )
    except ServiceError as exc:
        _raise_http_from_service_error(exc)

    return GenerationPublic.model_validate(generation)


@router.post("/", response_model=GenerationPublic)
def create_generation(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    generation_in: GenerationCreate,
) -> Any:
    try:
        generation = generation_service.create_generation_for_user(
            session=session,
            current_user=current_user,
            generation_in=generation_in,
        )
    except ServiceError as exc:
        _raise_http_from_service_error(exc)

    return GenerationPublic.model_validate(generation)


@router.patch("/{generation_id}", response_model=GenerationPublic)
def update_generation(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    generation_id: uuid.UUID,
    generation_in: GenerationUpdate,
) -> Any:
    try:
        generation = generation_service.update_generation_for_user(
            session=session,
            current_user=current_user,
            generation_id=generation_id,
            generation_in=generation_in,
        )
    except ServiceError as exc:
        _raise_http_from_service_error(exc)

    return GenerationPublic.model_validate(generation)
