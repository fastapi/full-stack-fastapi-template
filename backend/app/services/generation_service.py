import uuid

from sqlmodel import Session

from app.models import (
    ExtractVariablesRequest,
    ExtractVariablesResponse,
    Generation,
    GenerationCreate,
    GenerationUpdate,
    RenderTemplateRequest,
    RenderTemplateResponse,
    TemplateVariableConfig,
    User,
    get_datetime_utc,
)
from app.repositories import generation_repository
from app.services.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.template_utils import is_missing_value, normalize_variables_schema

from . import template_ai_service, template_service


def extract_values_for_user(
    *,
    session: Session,
    current_user: User,
    extract_in: ExtractVariablesRequest,
) -> ExtractVariablesResponse:
    template_version = template_service.get_template_version_for_user(
        session=session,
        current_user=current_user,
        template_version_id=extract_in.template_version_id,
    )

    normalized_schema = normalize_variables_schema(
        template_version.content,
        template_version.variables_schema,
    )

    values, missing_required, confidence, notes = template_ai_service.extract_variables(
        input_text=extract_in.input_text,
        variables_schema=normalized_schema,
        profile_context=extract_in.profile_context,
    )

    return ExtractVariablesResponse(
        values=values,
        missing_required=missing_required,
        confidence=confidence,
        notes=notes,
    )


def render_for_user(
    *,
    session: Session,
    current_user: User,
    render_in: RenderTemplateRequest,
) -> RenderTemplateResponse:
    template_version = template_service.get_template_version_for_user(
        session=session,
        current_user=current_user,
        template_version_id=render_in.template_version_id,
    )

    normalized_schema = normalize_variables_schema(
        template_version.content,
        template_version.variables_schema,
    )

    missing_required: list[str] = []
    for variable, raw_config in normalized_schema.items():
        config = TemplateVariableConfig.model_validate(raw_config)
        if config.required and is_missing_value(
            render_in.values.get(variable), config.type
        ):
            missing_required.append(variable)

    if missing_required:
        missing = ", ".join(missing_required)
        raise BadRequestError(f"Missing required variables: {missing}")

    style = render_in.style.model_dump() if render_in.style else {}
    output_text = template_ai_service.render_template(
        content=template_version.content,
        values=render_in.values,
        style=style,
    )
    return RenderTemplateResponse(output_text=output_text)


def list_generations_for_user(
    *, session: Session, current_user: User, skip: int = 0, limit: int = 100
) -> tuple[list[Generation], int]:
    return generation_repository.list_generations(
        session=session,
        user_id=current_user.id,
        is_superuser=current_user.is_superuser,
        skip=skip,
        limit=limit,
    )


def get_generation_for_user(
    *, session: Session, current_user: User, generation_id: uuid.UUID
) -> Generation:
    generation = generation_repository.get_generation_by_id(
        session=session, generation_id=generation_id
    )
    if generation is None:
        raise NotFoundError("Generation not found")
    if not current_user.is_superuser and generation.user_id != current_user.id:
        raise ForbiddenError("Not enough permissions")
    return generation


def create_generation_for_user(
    *, session: Session, current_user: User, generation_in: GenerationCreate
) -> Generation:
    template = template_service.get_template_for_user(
        session=session,
        current_user=current_user,
        template_id=generation_in.template_id,
    )
    template_version = template_service.get_template_version_for_user(
        session=session,
        current_user=current_user,
        template_version_id=generation_in.template_version_id,
    )

    if template_version.template_id != template.id:
        raise BadRequestError("template_version_id does not belong to template_id")

    generation = Generation.model_validate(
        generation_in,
        update={
            "user_id": current_user.id,
            "updated_at": get_datetime_utc(),
        },
    )
    return generation_repository.create_generation(
        session=session, generation=generation
    )


def update_generation_for_user(
    *,
    session: Session,
    current_user: User,
    generation_id: uuid.UUID,
    generation_in: GenerationUpdate,
) -> Generation:
    generation = get_generation_for_user(
        session=session,
        current_user=current_user,
        generation_id=generation_id,
    )

    update_data = generation_in.model_dump(exclude_unset=True)
    generation.sqlmodel_update(update_data)
    generation.updated_at = get_datetime_utc()

    return generation_repository.save_generation(session=session, generation=generation)
