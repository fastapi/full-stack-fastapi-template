"""Entity business logic and Supabase CRUD operations.

Provides service-layer functions for entity lifecycle management.
All functions accept a supabase Client as the first argument;
dependency injection happens at the route handler level.
"""

from postgrest.exceptions import APIError
from supabase import Client

from app.core.errors import ServiceError
from app.core.logging import get_logger
from app.models import EntitiesPublic, EntityCreate, EntityPublic, EntityUpdate

logger = get_logger(module=__name__)

_TABLE = "entities"

# Maximum number of entities that can be fetched in a single list call.
_MAX_LIMIT = 100


def create_entity(supabase: Client, data: EntityCreate, owner_id: str) -> EntityPublic:
    """Insert a new entity owned by owner_id. Returns EntityPublic.

    Args:
        supabase: Authenticated Supabase client.
        data: Validated creation payload.
        owner_id: Clerk user ID that will own the new entity.

    Returns:
        The newly created entity as :class:`~app.models.entity.EntityPublic`.

    Raises:
        ServiceError: 500 if the Supabase operation fails.
    """
    payload = {
        "title": data.title,
        "description": data.description,
        "owner_id": owner_id,
    }
    try:
        response = supabase.table(_TABLE).insert(payload).execute()
    except Exception as exc:
        logger.error("Failed to create entity", error=str(exc))
        raise ServiceError(
            status_code=500,
            message="Failed to create entity",
            code="ENTITY_CREATE_FAILED",
        ) from exc

    if not response.data:
        raise ServiceError(
            status_code=500,
            message="Entity insert returned no data",
            code="ENTITY_CREATE_FAILED",
        )

    return EntityPublic(**response.data[0])  # type: ignore[arg-type]


def get_entity(supabase: Client, entity_id: str, owner_id: str) -> EntityPublic:
    """Fetch a single entity by ID and owner.

    Args:
        supabase: Authenticated Supabase client.
        entity_id: UUID string of the entity to retrieve.
        owner_id: Clerk user ID used to enforce ownership.

    Returns:
        The matching entity as :class:`~app.models.entity.EntityPublic`.

    Raises:
        ServiceError: 404 if the entity does not exist or is not owned by owner_id.
        ServiceError: 500 if a database or network error occurs.
    """
    try:
        response = (
            supabase.table(_TABLE)
            .select("*")
            .eq("id", entity_id)
            .eq("owner_id", owner_id)
            .single()
            .execute()
        )
    except APIError as exc:
        raise ServiceError(
            status_code=404,
            message="Entity not found",
            code="ENTITY_NOT_FOUND",
        ) from exc
    except Exception as exc:
        logger.error("Failed to get entity", entity_id=entity_id, error=str(exc))
        raise ServiceError(
            status_code=500,
            message="Failed to retrieve entity",
            code="ENTITY_GET_FAILED",
        ) from exc

    return EntityPublic(**response.data)  # type: ignore[arg-type]


def list_entities(
    supabase: Client,
    owner_id: str,
    *,
    offset: int = 0,
    limit: int = 20,
) -> EntitiesPublic:
    """List entities for owner with pagination. Caps limit at 100.

    Args:
        supabase: Authenticated Supabase client.
        owner_id: Clerk user ID used to filter entities by ownership.
        offset: Zero-based index of the first record to return (default 0).
        limit: Maximum number of records to return (default 20, capped at 100).

    Returns:
        :class:`~app.models.entity.EntitiesPublic` with ``data`` list and total ``count``.

    Raises:
        ServiceError: 500 if the Supabase operation fails.
    """
    offset = max(0, offset)
    limit = max(1, min(limit, _MAX_LIMIT))
    end = offset + limit - 1

    try:
        response = (
            supabase.table(_TABLE)
            .select("*", count="exact")  # type: ignore[arg-type]
            .eq("owner_id", owner_id)
            .range(offset, end)
            .execute()
        )
    except Exception as exc:
        logger.error("Failed to list entities", error=str(exc))
        raise ServiceError(
            status_code=500,
            message="Failed to list entities",
            code="ENTITY_LIST_FAILED",
        ) from exc

    items = [EntityPublic(**row) for row in response.data]  # type: ignore[arg-type]
    return EntitiesPublic(data=items, count=response.count or 0)


def update_entity(
    supabase: Client,
    entity_id: str,
    owner_id: str,
    data: EntityUpdate,
) -> EntityPublic:
    """Partially update an entity. Raises ServiceError(404) if not found or not owned.

    When ``data`` contains no fields (all values are unset), the function skips the
    UPDATE call and returns the current entity unchanged.

    Args:
        supabase: Authenticated Supabase client.
        entity_id: UUID string of the entity to update.
        owner_id: Clerk user ID used to enforce ownership.
        data: Partial update payload. Only provided fields are written.

    Returns:
        The updated (or unchanged) entity as :class:`~app.models.entity.EntityPublic`.

    Raises:
        ServiceError: 404 if the entity does not exist or is not owned by owner_id.
        ServiceError: 500 if the Supabase operation fails.
    """
    fields = data.model_dump(exclude_unset=True)

    # No-op: no fields provided — fetch and return the current entity.
    if not fields:
        return get_entity(supabase, entity_id, owner_id)

    try:
        response = (
            supabase.table(_TABLE)
            .update(fields)
            .eq("id", entity_id)
            .eq("owner_id", owner_id)
            .execute()
        )
    except Exception as exc:
        logger.error("Failed to update entity", entity_id=entity_id, error=str(exc))
        raise ServiceError(
            status_code=500,
            message="Failed to update entity",
            code="ENTITY_UPDATE_FAILED",
        ) from exc

    if not response.data:
        raise ServiceError(
            status_code=404,
            message="Entity not found",
            code="ENTITY_NOT_FOUND",
        )

    return EntityPublic(**response.data[0])  # type: ignore[arg-type]


def delete_entity(supabase: Client, entity_id: str, owner_id: str) -> None:
    """Delete an entity. Raises ServiceError(404) if not found or not owned.

    Args:
        supabase: Authenticated Supabase client.
        entity_id: UUID string of the entity to delete.
        owner_id: Clerk user ID used to enforce ownership.

    Returns:
        None on success.

    Raises:
        ServiceError: 404 if the entity does not exist or is not owned by owner_id.
        ServiceError: 500 if the Supabase operation fails.
    """
    try:
        response = (
            supabase.table(_TABLE)
            .delete()
            .eq("id", entity_id)
            .eq("owner_id", owner_id)
            .execute()
        )
    except Exception as exc:
        logger.error("Failed to delete entity", entity_id=entity_id, error=str(exc))
        raise ServiceError(
            status_code=500,
            message="Failed to delete entity",
            code="ENTITY_DELETE_FAILED",
        ) from exc

    if not response.data:
        raise ServiceError(
            status_code=404,
            message="Entity not found",
            code="ENTITY_NOT_FOUND",
        )
