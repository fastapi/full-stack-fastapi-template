import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    CategoryTranslationUpdate,
    Message,
    RaceCategoriesPublic,
    RaceCategoryCreate,
    RaceCategoryPublic,
    RaceCategoryPublicWithDetails,
    RaceCategoryUpdate,
)

router = APIRouter(prefix="/race-categories", tags=["race-categories"])


@router.get("/", response_model=RaceCategoriesPublic)
def read_race_categories(
    session: SessionDep,
    race_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve race categories for a specific race. Public endpoint.
    """
    categories = crud.get_race_categories(
        session=session, race_id=race_id, skip=skip, limit=limit
    )

    # Add computed fields for public response
    enriched_categories = []
    race = crud.get_race(session=session, race_id=race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    for category in categories:
        registration_count = crud.get_category_registration_count(
            session=session, category_id=category.id
        )
        available_spots = crud.get_category_available_spots(
            session=session,
            category_id=category.id,
            max_participants=category.max_participants,
        )
        is_registration_open = crud.is_category_registration_open(
            category=category, race=race, session=session
        )
        current_price = crud.get_category_current_price(category=category, race=race)

        enriched_category = RaceCategoryPublicWithDetails(
            **category.model_dump(),
            registration_count=registration_count,
            available_spots=available_spots,
            is_registration_open=is_registration_open,
            current_price=current_price,
        )
        enriched_categories.append(enriched_category)

    return RaceCategoriesPublic(
        data=enriched_categories, count=len(enriched_categories)
    )


@router.get("/{category_id}", response_model=RaceCategoryPublicWithDetails)
def read_race_category(session: SessionDep, category_id: uuid.UUID) -> Any:
    """
    Get race category by ID with details. Public endpoint.
    """
    category = crud.get_race_category(session=session, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Race category not found")

    race = crud.get_race(session=session, race_id=category.race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    # Add computed fields
    registration_count = crud.get_category_registration_count(
        session=session, category_id=category.id
    )
    available_spots = crud.get_category_available_spots(
        session=session,
        category_id=category.id,
        max_participants=category.max_participants,
    )
    is_registration_open = crud.is_category_registration_open(
        category=category, race=race, session=session
    )
    current_price = crud.get_category_current_price(category=category, race=race)

    return RaceCategoryPublicWithDetails(
        **category.model_dump(),
        registration_count=registration_count,
        available_spots=available_spots,
        is_registration_open=is_registration_open,
        current_price=current_price,
    )


@router.post("/", response_model=RaceCategoryPublic)
def create_race_category(
    *, session: SessionDep, current_user: CurrentUser, category_in: RaceCategoryCreate
) -> Any:
    """
    Create new race category.
    Only the race organizer or admin can create categories.
    """
    # Get the race to check permissions
    race = crud.get_race(session=session, race_id=category_in.race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    # Check permissions
    if not current_user.is_superuser and race.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    category = crud.create_race_category(session=session, category_in=category_in)
    return category


@router.put("/{category_id}", response_model=RaceCategoryPublic)
def update_race_category(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    category_id: uuid.UUID,
    category_in: RaceCategoryUpdate,
) -> Any:
    """
    Update a race category.
    Only the race organizer or admin can update.
    """
    category = crud.get_race_category(session=session, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Race category not found")

    # Get the race to check permissions
    race = crud.get_race(session=session, race_id=category.race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    # Check permissions
    if not current_user.is_superuser and race.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    category = crud.update_race_category(
        session=session, db_category=category, category_in=category_in
    )
    return category


@router.delete("/{category_id}", response_model=Message)
def delete_race_category(
    *, session: SessionDep, current_user: CurrentUser, category_id: uuid.UUID
) -> Any:
    """
    Delete a race category.
    Only the race organizer or admin can delete.
    """
    category = crud.get_race_category(session=session, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Race category not found")

    # Get the race to check permissions
    race = crud.get_race(session=session, race_id=category.race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    # Check permissions
    if not current_user.is_superuser and race.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud.delete_race_category(session=session, category_id=category_id)
    return Message(message="Race category deleted successfully")


@router.put("/{category_id}/translations", response_model=RaceCategoryPublic)
def update_category_translations(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    category_id: uuid.UUID,
    translation: CategoryTranslationUpdate,
) -> Any:
    """
    Update translations for a race category.
    Only race organizer or admin can update translations.
    """
    from app.i18n import is_language_supported, set_translation
    
    # Get the category
    category = crud.get_race_category(session=session, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Race category not found")
    
    # Get the race to check permissions
    race = crud.get_race(session=session, race_id=category.race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    # Check permissions - only organizer or admin
    if race.organizer_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only race organizer or admin can update translations"
        )
    
    # Validate language
    if not is_language_supported(translation.language):
        raise HTTPException(
            status_code=400,
            detail=f"Language '{translation.language}' is not supported"
        )
    
    # Update translations
    if translation.name:
        set_translation(category, "name", translation.name, translation.language)
    if translation.description:
        set_translation(category, "description", translation.description, translation.language)
    
    session.add(category)
    session.commit()
    session.refresh(category)
    
    return category


@router.get("/{category_id}/translations", response_model=dict[str, Any])
def get_category_translations(
    *,
    session: SessionDep,
    category_id: uuid.UUID,
) -> Any:
    """
    Get all translations for a race category.
    Public endpoint - anyone can view translations.
    """
    category = crud.get_race_category(session=session, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Race category not found")
    
    return category.translations or {}

