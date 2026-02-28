"""Entity CRUD route handlers.

Thin routes that inject authentication and database dependencies, then
delegate all business logic to :mod:`app.services.entity_service`.
"""

import uuid

from fastapi import APIRouter, Query, Response

from app.api.deps import PrincipalDep, SupabaseDep
from app.models import EntitiesPublic, EntityCreate, EntityPublic, EntityUpdate
from app.services import entity_service

router = APIRouter(prefix="/entities", tags=["entities"])


@router.post("/", response_model=EntityPublic, status_code=201)
def create_entity(
    supabase: SupabaseDep,
    principal: PrincipalDep,
    data: EntityCreate,
) -> EntityPublic:
    """Create a new entity owned by the authenticated user."""
    return entity_service.create_entity(supabase, data, principal.user_id)


@router.get("/", response_model=EntitiesPublic)
def list_entities(
    supabase: SupabaseDep,
    principal: PrincipalDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> EntitiesPublic:
    """List entities owned by the authenticated user with pagination."""
    return entity_service.list_entities(
        supabase, principal.user_id, offset=offset, limit=limit
    )


@router.get("/{entity_id}", response_model=EntityPublic)
def get_entity(
    supabase: SupabaseDep,
    principal: PrincipalDep,
    entity_id: uuid.UUID,
) -> EntityPublic:
    """Retrieve a single entity by ID."""
    return entity_service.get_entity(supabase, str(entity_id), principal.user_id)


@router.patch("/{entity_id}", response_model=EntityPublic)
def update_entity(
    supabase: SupabaseDep,
    principal: PrincipalDep,
    entity_id: uuid.UUID,
    data: EntityUpdate,
) -> EntityPublic:
    """Partially update an entity."""
    return entity_service.update_entity(
        supabase, str(entity_id), principal.user_id, data
    )


@router.delete("/{entity_id}", status_code=204)
def delete_entity(
    supabase: SupabaseDep,
    principal: PrincipalDep,
    entity_id: uuid.UUID,
) -> Response:
    """Delete an entity."""
    entity_service.delete_entity(supabase, str(entity_id), principal.user_id)
    return Response(status_code=204)
