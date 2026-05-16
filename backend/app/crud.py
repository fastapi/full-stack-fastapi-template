import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import or_
from sqlmodel import Session, col, func, select, text

from app.core.security import get_password_hash, verify_password
from app.models import (
    DifficultyEnum,
    DistancePrefEnum,
    InteractionTypeEnum,
    Item,
    ItemCreate,
    MediaAsset,
    MediaAssetCreate,
    MediaAssetUpdate,
    Province,
    Race,
    RaceAttribute,
    RaceAttributeCreate,
    RaceAttributeUpdate,
    RaceCategory,
    RaceCategoryCreate,
    RaceCategoryUpdate,
    RaceCheckpoint,
    RaceCheckpointCreate,
    RaceCheckpointUpdate,
    RaceCreate,
    RaceRegistration,
    RaceRegistrationCreate,
    RaceRegistrationUpdate,
    RaceResult,
    RaceResultCreate,
    RaceResultUpdate,
    RaceSplitTime,
    RaceSplitTimeCreate,
    RaceStatusEnum,
    RaceTag,
    RaceTagCreate,
    RaceTagLink,
    RaceUpdate,
    Role,
    RoleCreate,
    TerrainEnum,
    User,
    UserCreate,
    UserProfile,
    UserProfileCreate,
    UserProfileUpdate,
    UserRaceInteraction,
    UserUpdate,
    Ward,
)


# Role CRUD operations
def create_role(*, session: Session, role_create: RoleCreate) -> Role:
    db_obj = Role.model_validate(role_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_role_by_name(*, session: Session, name: str) -> Role | None:
    statement = select(Role).where(Role.name == name)
    return session.exec(statement).first()


def get_or_create_role(
    *, session: Session, role_name: str, description: str | None = None
) -> Role:
    """Get existing role or create it if it doesn't exist."""
    role = get_role_by_name(session=session, name=role_name)
    if not role:
        role = create_role(
            session=session,
            role_create=RoleCreate(name=role_name, description=description),
        )
    return role


def assign_role_to_user(*, session: Session, user: User, role: Role) -> User:
    """Assign a role to a user."""
    if role not in user.roles:
        user.roles.append(role)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


def remove_role_from_user(*, session: Session, user: User, role: Role) -> User:
    """Remove a role from a user."""
    if role in user.roles:
        user.roles.remove(role)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


def user_has_role(user: User, role_name: str) -> bool:
    """Check if user has a specific role."""
    return any(role.name == role_name for role in user.roles)


def user_has_any_role(user: User, role_names: list[str]) -> bool:
    """Check if user has any of the specified roles."""
    return any(role.name in role_names for role in user.roles)


# User CRUD operations


def create_user(
    *, session: Session, user_create: UserCreate, default_role: str | None = "runner"
) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    # Assign default role if specified
    if default_role:
        role = get_role_by_name(session=session, name=default_role)
        if role:
            assign_role_to_user(session=session, user=db_obj, role=role)

    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


# Dummy hash to use for timing attack prevention when user is not found
# This is an Argon2 hash of a random password, used to ensure constant-time comparison
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        # Prevent timing attacks by running password verification even when user doesn't exist
        # This ensures the response time is similar whether or not the email exists
        verify_password(password, DUMMY_HASH)
        return None
    verified, updated_password_hash = verify_password(password, db_user.hashed_password)
    if not verified:
        return None
    if updated_password_hash:
        db_user.hashed_password = updated_password_hash
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# =============================================================================
# Race CRUD operations
# =============================================================================


def create_race(
    *, session: Session, race_in: RaceCreate, organizer_id: uuid.UUID
) -> Race:
    """Create a new race."""
    race_data = race_in.model_dump()
    
    # Populate province_name if province_code is provided
    if race_data.get("province_code"):
        province = session.get(Province, race_data["province_code"])
        if province:
            race_data["province_name"] = province.name
    
    # Populate ward_name if ward_code is provided
    if race_data.get("ward_code"):
        ward = session.get(Ward, race_data["ward_code"])
        if ward:
            race_data["ward_name"] = ward.name
    
    # Set country_code for Vietnam races
    if race_data.get("country") == "Vietnam" or not race_data.get("country_code"):
        race_data["country_code"] = "VN"
    
    db_race = Race.model_validate(race_data, update={"organizer_id": organizer_id})
    session.add(db_race)
    session.commit()
    session.refresh(db_race)
    return db_race


def get_race(*, session: Session, race_id: uuid.UUID) -> Race | None:
    """Get a race by ID."""
    return session.get(Race, race_id)


def get_races(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    organizer_id: uuid.UUID | None = None,
) -> list[Race]:
    """Get races with pagination, optionally filtered by organizer."""
    statement = select(Race).offset(skip).limit(limit)
    if organizer_id:
        statement = statement.where(Race.organizer_id == organizer_id)
    statement = statement.order_by(col(Race.event_start_date).desc())
    return list(session.exec(statement).all())


def get_races_count(*, session: Session, organizer_id: uuid.UUID | None = None) -> int:
    """Get total count of races."""
    statement = select(func.count(Race.id))
    if organizer_id:
        statement = statement.where(Race.organizer_id == organizer_id)
    return session.exec(statement).one()


def update_race(*, session: Session, db_race: Race, race_in: RaceUpdate) -> Race:
    """Update a race."""
    race_data = race_in.model_dump(exclude_unset=True)
    tag_ids = race_data.pop("tag_ids", None)
    
    # Populate province_name if province_code is being updated
    if "province_code" in race_data and race_data["province_code"]:
        province = session.get(Province, race_data["province_code"])
        if province:
            race_data["province_name"] = province.name
    elif "province_code" in race_data and race_data["province_code"] is None:
        # Clear province_name if province_code is being cleared
        race_data["province_name"] = None
    
    # Populate ward_name if ward_code is being updated
    if "ward_code" in race_data and race_data["ward_code"]:
        ward = session.get(Ward, race_data["ward_code"])
        if ward:
            race_data["ward_name"] = ward.name
    elif "ward_code" in race_data and race_data["ward_code"] is None:
        # Clear ward_name if ward_code is being cleared
        race_data["ward_name"] = None
    
    # Update country_code if country is being updated to Vietnam
    if "country" in race_data:
        if race_data["country"] == "Vietnam":
            race_data["country_code"] = "VN"
        elif race_data["country"] is None:
            race_data["country_code"] = None
    
    race_data["updated_at"] = datetime.now(timezone.utc)
    db_race.sqlmodel_update(race_data)
    session.add(db_race)
    session.commit()
    session.refresh(db_race)
    if tag_ids is not None:
        set_race_tags(session=session, race=db_race, tag_ids=tag_ids)
    return db_race


def delete_race(*, session: Session, race_id: uuid.UUID) -> bool:
    """Delete a race."""
    race = session.get(Race, race_id)
    if race:
        session.delete(race)
        session.commit()
        return True
    return False


def update_race_embedding(
    *, session: Session, race_id: uuid.UUID, embedding: list[float]
) -> None:
    """Persist a pre-computed embedding vector on a race row."""
    race = session.get(Race, race_id)
    if race:
        race.embedding = embedding
        session.add(race)
        session.commit()


def get_races_without_embedding(
    *, session: Session, limit: int = 100
) -> list[Race]:
    """Return races that have no embedding yet (for batch reindexing)."""
    return list(
        session.exec(select(Race).where(Race.embedding == None).limit(limit)).all()  # noqa: E711
    )


# =============================================================================
# MediaAsset CRUD operations
# =============================================================================


def create_media_asset(*, session: Session, media_in: MediaAssetCreate) -> MediaAsset:
    """Create a media asset."""
    db_media = MediaAsset.model_validate(media_in)
    session.add(db_media)
    session.commit()
    session.refresh(db_media)
    return db_media


def get_media_asset(*, session: Session, media_id: uuid.UUID) -> MediaAsset | None:
    """Get a media asset by ID."""
    return session.get(MediaAsset, media_id)


def get_media_assets(
    *,
    session: Session,
    content_type: str | None = None,
    content_id: uuid.UUID | None = None,
    kind: str | None = None,
    is_public: bool | None = None,
    skip: int = 0,
    limit: int = 200,
) -> list[MediaAsset]:
    """Get media assets with optional filtering."""
    statement = select(MediaAsset)
    if content_type:
        statement = statement.where(MediaAsset.content_type == content_type)
    if content_id:
        statement = statement.where(MediaAsset.content_id == content_id)
    if kind:
        statement = statement.where(MediaAsset.kind == kind)
    if is_public is not None:
        statement = statement.where(MediaAsset.is_public == is_public)

    statement = (
        statement.order_by(
            col(MediaAsset.display_order),
            col(MediaAsset.created_at).desc(),
        )
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def get_media_assets_count(
    *,
    session: Session,
    content_type: str | None = None,
    content_id: uuid.UUID | None = None,
    kind: str | None = None,
    is_public: bool | None = None,
) -> int:
    """Get count of media assets with optional filtering."""
    statement = select(func.count(MediaAsset.id))
    if content_type:
        statement = statement.where(MediaAsset.content_type == content_type)
    if content_id:
        statement = statement.where(MediaAsset.content_id == content_id)
    if kind:
        statement = statement.where(MediaAsset.kind == kind)
    if is_public is not None:
        statement = statement.where(MediaAsset.is_public == is_public)
    return session.exec(statement).one()


def clear_primary_media(
    *,
    session: Session,
    content_type: str,
    content_id: uuid.UUID,
    kind: str,
    exclude_id: uuid.UUID | None = None,
) -> None:
    """Ensure only one media item is primary for a given content_type/content_id/kind."""
    statement = select(MediaAsset).where(
        MediaAsset.content_type == content_type,
        MediaAsset.content_id == content_id,
        MediaAsset.kind == kind,
        MediaAsset.is_primary,
    )
    if exclude_id:
        statement = statement.where(MediaAsset.id != exclude_id)

    existing_primary = list(session.exec(statement).all())
    for media in existing_primary:
        media.is_primary = False
        media.updated_at = datetime.now(timezone.utc)
        session.add(media)
    if existing_primary:
        session.commit()


def update_media_asset(
    *, session: Session, db_media: MediaAsset, media_in: MediaAssetUpdate
) -> MediaAsset:
    """Update a media asset."""
    media_data = media_in.model_dump(exclude_unset=True)
    media_data["updated_at"] = datetime.now(timezone.utc)
    db_media.sqlmodel_update(media_data)
    session.add(db_media)
    session.commit()
    session.refresh(db_media)
    return db_media


def delete_media_asset(*, session: Session, media_id: uuid.UUID) -> bool:
    """Delete a media asset."""
    media = session.get(MediaAsset, media_id)
    if media:
        session.delete(media)
        session.commit()
        return True
    return False


# =============================================================================
# RaceCategory CRUD operations
# =============================================================================


def create_race_category(
    *, session: Session, category_in: RaceCategoryCreate
) -> RaceCategory:
    """Create a new race category."""
    db_category = RaceCategory.model_validate(category_in)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


def get_race_category(
    *, session: Session, category_id: uuid.UUID
) -> RaceCategory | None:
    """Get a race category by ID."""
    return session.get(RaceCategory, category_id)


def get_race_categories(
    *, session: Session, race_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[RaceCategory]:
    """Get all categories for a race."""
    statement = (
        select(RaceCategory)
        .where(RaceCategory.race_id == race_id)
        .order_by(col(RaceCategory.display_order), col(RaceCategory.distance_km))
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def update_race_category(
    *, session: Session, db_category: RaceCategory, category_in: RaceCategoryUpdate
) -> RaceCategory:
    """Update a race category."""
    category_data = category_in.model_dump(exclude_unset=True)
    category_data["updated_at"] = datetime.now(timezone.utc)
    db_category.sqlmodel_update(category_data)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


def delete_race_category(*, session: Session, category_id: uuid.UUID) -> bool:
    """Delete a race category."""
    category = session.get(RaceCategory, category_id)
    if category:
        session.delete(category)
        session.commit()
        return True
    return False


def get_category_registration_count(*, session: Session, category_id: uuid.UUID) -> int:
    """Get registration count for a category."""
    statement = select(func.count(RaceRegistration.id)).where(
        RaceRegistration.category_id == category_id
    )
    return session.exec(statement).one()


def get_category_registration_window(
    category: RaceCategory, race: Race
) -> tuple[datetime | None, datetime | None]:
    """
    Get effective registration start/end for a category.
    Category-specific dates override race defaults.
    """
    start = category.registration_start or race.registration_start
    end = category.registration_end or race.registration_end
    return start, end


def is_category_registration_open(
    category: RaceCategory,
    race: Race,
    session: Session,
    check_time: datetime | None = None,
) -> bool:
    """Check if registration is currently open for a category."""
    if check_time is None:
        check_time = datetime.now(timezone.utc)

    start, end = get_category_registration_window(category, race)

    # Check if within registration window
    if start and check_time < start:
        return False
    if end and check_time > end:
        return False

    # Check if category is full
    if category.max_participants:
        count = get_category_registration_count(
            session=session, category_id=category.id
        )
        if count >= category.max_participants:
            return False

    # Check if category and race are active
    if not category.is_active or not race.is_active:
        return False

    return True


def get_category_current_price(
    category: RaceCategory, race: Race, check_time: datetime | None = None
) -> float | None:
    """
    Get current price for a category.
    Returns early bird price if applicable, otherwise regular price.
    """
    if check_time is None:
        check_time = datetime.now(timezone.utc)

    # Check early bird pricing
    if (
        category.early_bird_price is not None
        and category.early_bird_deadline
        and check_time <= category.early_bird_deadline
    ):
        return category.early_bird_price

    # Return category price or race default
    return category.price or race.base_price


def get_category_available_spots(
    *, session: Session, category_id: uuid.UUID, max_participants: int | None
) -> int | None:
    """Get number of available spots for a category."""
    if max_participants is None:
        return None

    count = get_category_registration_count(session=session, category_id=category_id)
    return max(0, max_participants - count)


# =============================================================================
# RaceRegistration CRUD operations
# =============================================================================


def create_race_registration(
    *,
    session: Session,
    registration_in: RaceRegistrationCreate,
    runner_id: uuid.UUID,
) -> RaceRegistration:
    """Create a new race registration."""
    db_registration = RaceRegistration.model_validate(
        registration_in, update={"runner_id": runner_id}
    )
    session.add(db_registration)
    session.commit()
    session.refresh(db_registration)
    return db_registration


def get_race_registration(
    *, session: Session, registration_id: uuid.UUID
) -> RaceRegistration | None:
    """Get a race registration by ID."""
    return session.get(RaceRegistration, registration_id)


def get_race_registrations(
    *,
    session: Session,
    race_id: uuid.UUID | None = None,
    runner_id: uuid.UUID | None = None,
    category_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[RaceRegistration]:
    """Get race registrations with filters."""
    statement = select(RaceRegistration).offset(skip).limit(limit)

    if race_id:
        statement = statement.where(RaceRegistration.race_id == race_id)
    if runner_id:
        statement = statement.where(RaceRegistration.runner_id == runner_id)
    if category_id:
        statement = statement.where(RaceRegistration.category_id == category_id)

    statement = statement.order_by(col(RaceRegistration.registered_at).desc())
    return list(session.exec(statement).all())


def get_race_registrations_count(
    *,
    session: Session,
    race_id: uuid.UUID | None = None,
    runner_id: uuid.UUID | None = None,
    category_id: uuid.UUID | None = None,
) -> int:
    """Get count of race registrations with filters."""
    statement = select(func.count(RaceRegistration.id))

    if race_id:
        statement = statement.where(RaceRegistration.race_id == race_id)
    if runner_id:
        statement = statement.where(RaceRegistration.runner_id == runner_id)
    if category_id:
        statement = statement.where(RaceRegistration.category_id == category_id)

    return session.exec(statement).one()


def update_race_registration(
    *,
    session: Session,
    db_registration: RaceRegistration,
    registration_in: RaceRegistrationUpdate,
) -> RaceRegistration:
    """Update a race registration."""
    registration_data = registration_in.model_dump(exclude_unset=True)
    registration_data["updated_at"] = datetime.now(timezone.utc)
    db_registration.sqlmodel_update(registration_data)
    session.add(db_registration)
    session.commit()
    session.refresh(db_registration)
    return db_registration


def delete_race_registration(*, session: Session, registration_id: uuid.UUID) -> bool:
    """Delete a race registration."""
    registration = session.get(RaceRegistration, registration_id)
    if registration:
        session.delete(registration)
        session.commit()
        return True
    return False


def check_existing_registration(
    *, session: Session, runner_id: uuid.UUID, race_id: uuid.UUID
) -> RaceRegistration | None:
    """Check if a runner is already registered for a race."""
    statement = select(RaceRegistration).where(
        RaceRegistration.runner_id == runner_id,
        RaceRegistration.race_id == race_id,
    )
    return session.exec(statement).first()


# =============================================================================
# RaceResult CRUD operations
# =============================================================================


def create_race_result(*, session: Session, result_in: RaceResultCreate) -> RaceResult:
    """Create a new race result."""
    db_result = RaceResult.model_validate(result_in)
    session.add(db_result)
    session.commit()
    session.refresh(db_result)
    return db_result


def get_race_result(*, session: Session, result_id: uuid.UUID) -> RaceResult | None:
    """Get a race result by ID."""
    return session.get(RaceResult, result_id)


def get_race_result_by_registration(
    *, session: Session, registration_id: uuid.UUID
) -> RaceResult | None:
    """Get race result by registration ID."""
    statement = select(RaceResult).where(RaceResult.registration_id == registration_id)
    return session.exec(statement).first()


def get_race_results(
    *, session: Session, race_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[RaceResult]:
    """Get all results for a race."""
    statement = (
        select(RaceResult)
        .join(RaceRegistration)
        .where(RaceRegistration.race_id == race_id)
        .order_by(col(RaceResult.overall_position))
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def update_race_result(
    *, session: Session, db_result: RaceResult, result_in: RaceResultUpdate
) -> RaceResult:
    """Update a race result."""
    result_data = result_in.model_dump(exclude_unset=True)
    result_data["updated_at"] = datetime.now(timezone.utc)
    db_result.sqlmodel_update(result_data)
    session.add(db_result)
    session.commit()
    session.refresh(db_result)
    return db_result


def delete_race_result(*, session: Session, result_id: uuid.UUID) -> bool:
    """Delete a race result."""
    result = session.get(RaceResult, result_id)
    if result:
        session.delete(result)
        session.commit()
        return True
    return False


# =============================================================================
# RaceAttribute CRUD operations
# =============================================================================


def create_race_attribute(
    *, session: Session, attribute_in: RaceAttributeCreate
) -> RaceAttribute:
    """Create a new race attribute."""
    db_attribute = RaceAttribute.model_validate(attribute_in)
    session.add(db_attribute)
    session.commit()
    session.refresh(db_attribute)
    return db_attribute


def get_race_attribute(
    *, session: Session, attribute_id: uuid.UUID
) -> RaceAttribute | None:
    """Get a race attribute by ID."""
    return session.get(RaceAttribute, attribute_id)


def get_race_attributes(
    *, session: Session, race_id: uuid.UUID, is_public: bool | None = None
) -> list[RaceAttribute]:
    """Get all attributes for a race."""
    statement = select(RaceAttribute).where(RaceAttribute.race_id == race_id)

    if is_public is not None:
        statement = statement.where(RaceAttribute.is_public == is_public)

    statement = statement.order_by(
        col(RaceAttribute.display_order), col(RaceAttribute.key)
    )
    return list(session.exec(statement).all())


def update_race_attribute(
    *, session: Session, db_attribute: RaceAttribute, attribute_in: RaceAttributeUpdate
) -> RaceAttribute:
    """Update a race attribute."""
    attribute_data = attribute_in.model_dump(exclude_unset=True)
    attribute_data["updated_at"] = datetime.now(timezone.utc)
    db_attribute.sqlmodel_update(attribute_data)
    session.add(db_attribute)
    session.commit()
    session.refresh(db_attribute)
    return db_attribute


def delete_race_attribute(*, session: Session, attribute_id: uuid.UUID) -> bool:
    """Delete a race attribute."""
    attribute = session.get(RaceAttribute, attribute_id)
    if attribute:
        session.delete(attribute)
        session.commit()
        return True
    return False


# =============================================================================
# RaceCheckpoint and SplitTime CRUD operations
# =============================================================================


def create_race_checkpoint(
    *, session: Session, checkpoint_in: RaceCheckpointCreate
) -> RaceCheckpoint:
    """Create a new race checkpoint."""
    db_checkpoint = RaceCheckpoint.model_validate(checkpoint_in)
    session.add(db_checkpoint)
    session.commit()
    session.refresh(db_checkpoint)
    return db_checkpoint


def get_race_checkpoint(
    *, session: Session, checkpoint_id: uuid.UUID
) -> RaceCheckpoint | None:
    """Get a race checkpoint by ID."""
    return session.get(RaceCheckpoint, checkpoint_id)


def get_race_checkpoints(
    *, session: Session, race_id: uuid.UUID
) -> list[RaceCheckpoint]:
    """Get all checkpoints for a race."""
    statement = (
        select(RaceCheckpoint)
        .where(RaceCheckpoint.race_id == race_id)
        .order_by(col(RaceCheckpoint.sequence))
    )
    return list(session.exec(statement).all())


def update_race_checkpoint(
    *,
    session: Session,
    db_checkpoint: RaceCheckpoint,
    checkpoint_in: RaceCheckpointUpdate,
) -> RaceCheckpoint:
    """Update a race checkpoint."""
    checkpoint_data = checkpoint_in.model_dump(exclude_unset=True)
    db_checkpoint.sqlmodel_update(checkpoint_data)
    session.add(db_checkpoint)
    session.commit()
    session.refresh(db_checkpoint)
    return db_checkpoint


def delete_race_checkpoint(*, session: Session, checkpoint_id: uuid.UUID) -> bool:
    """Delete a race checkpoint."""
    checkpoint = session.get(RaceCheckpoint, checkpoint_id)
    if checkpoint:
        session.delete(checkpoint)
        session.commit()
        return True
    return False


def create_race_split_time(
    *, session: Session, split_time_in: RaceSplitTimeCreate
) -> RaceSplitTime:
    """Create a new split time."""
    db_split_time = RaceSplitTime.model_validate(split_time_in)
    session.add(db_split_time)
    session.commit()
    session.refresh(db_split_time)
    return db_split_time


def get_registration_split_times(
    *, session: Session, registration_id: uuid.UUID
) -> list[RaceSplitTime]:
    """Get all split times for a registration."""
    statement = (
        select(RaceSplitTime)
        .where(RaceSplitTime.registration_id == registration_id)
        .order_by(col(RaceSplitTime.recorded_at))
    )
    return list(session.exec(statement).all())


# =============================================================================
# RaceTag CRUD operations
# =============================================================================


def get_tag_by_slug(*, session: Session, slug: str) -> RaceTag | None:
    return session.exec(select(RaceTag).where(RaceTag.slug == slug)).first()


def get_all_tags(*, session: Session) -> list[RaceTag]:
    return list(session.exec(select(RaceTag).order_by(col(RaceTag.name))).all())


def get_all_tags_count(*, session: Session) -> int:
    return session.exec(select(func.count(RaceTag.id))).one()


def get_or_create_tag(*, session: Session, tag_in: RaceTagCreate) -> RaceTag:
    tag = get_tag_by_slug(session=session, slug=tag_in.slug)
    if not tag:
        tag = RaceTag.model_validate(tag_in)
        session.add(tag)
        session.commit()
        session.refresh(tag)
    return tag


def get_race_tags(*, session: Session, race_id: uuid.UUID) -> list[RaceTag]:
    linked_ids = select(RaceTagLink.tag_id).where(RaceTagLink.race_id == race_id)
    statement = (
        select(RaceTag)
        .where(col(RaceTag.id).in_(linked_ids))
        .order_by(col(RaceTag.name))
    )
    return list(session.exec(statement).all())


def set_race_tags(
    *, session: Session, race: Race, tag_ids: list[uuid.UUID]
) -> Race:
    """Replace the full tag set for a race."""
    existing = session.exec(
        select(RaceTagLink).where(RaceTagLink.race_id == race.id)
    ).all()
    for link in existing:
        session.delete(link)
    session.flush()

    # Add new links
    for tag_id in tag_ids:
        session.add(RaceTagLink(race_id=race.id, tag_id=tag_id))
    session.commit()
    session.refresh(race)
    return race


# =============================================================================
# UserProfile CRUD operations
# =============================================================================


def get_user_profile(*, session: Session, user_id: uuid.UUID) -> UserProfile | None:
    return session.exec(
        select(UserProfile).where(UserProfile.user_id == user_id)
    ).first()


def upsert_user_profile(
    *, session: Session, user_id: uuid.UUID, profile_in: UserProfileCreate
) -> UserProfile:
    """Create or fully replace the profile for a user."""
    profile = get_user_profile(session=session, user_id=user_id)
    if profile:
        profile_data = profile_in.model_dump(exclude_unset=True)
        profile_data["updated_at"] = datetime.now(timezone.utc)
        profile.sqlmodel_update(profile_data)
    else:
        profile = UserProfile.model_validate(profile_in, update={"user_id": user_id})
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def update_user_profile(
    *, session: Session, db_profile: UserProfile, profile_in: UserProfileUpdate
) -> UserProfile:
    profile_data = profile_in.model_dump(exclude_unset=True)
    profile_data["updated_at"] = datetime.now(timezone.utc)
    db_profile.sqlmodel_update(profile_data)
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile


def delete_user_profile(*, session: Session, user_id: uuid.UUID) -> bool:
    profile = get_user_profile(session=session, user_id=user_id)
    if profile:
        session.delete(profile)
        session.commit()
        return True
    return False


# =============================================================================
# UserRaceInteraction CRUD operations
# =============================================================================


def record_interaction(
    *,
    session: Session,
    user_id: uuid.UUID,
    race_id: uuid.UUID,
    action: InteractionTypeEnum,
) -> UserRaceInteraction:
    interaction = UserRaceInteraction(
        user_id=user_id, race_id=race_id, action=action
    )
    session.add(interaction)
    session.commit()
    session.refresh(interaction)
    return interaction


def get_user_interaction(
    *, session: Session, user_id: uuid.UUID, race_id: uuid.UUID, action: InteractionTypeEnum
) -> UserRaceInteraction | None:
    return session.exec(
        select(UserRaceInteraction).where(
            UserRaceInteraction.user_id == user_id,
            UserRaceInteraction.race_id == race_id,
            UserRaceInteraction.action == action,
        )
    ).first()


def get_user_saved_races(*, session: Session, user_id: uuid.UUID) -> list[Race]:
    """Return races the user has saved (most recent first)."""
    saved_ids = (
        select(UserRaceInteraction.race_id)
        .where(
            UserRaceInteraction.user_id == user_id,
            UserRaceInteraction.action == InteractionTypeEnum.SAVED,
        )
    )
    statement = (
        select(Race)
        .where(col(Race.id).in_(saved_ids))
        .order_by(col(Race.event_start_date).desc())
    )
    return list(session.exec(statement).all())


def get_interaction_counts(
    *, session: Session, race_id: uuid.UUID
) -> dict[str, int]:
    """Return interaction counts per action type for a race."""
    rows = session.exec(
        select(UserRaceInteraction.action, func.count(UserRaceInteraction.id))
        .where(UserRaceInteraction.race_id == race_id)
        .group_by(UserRaceInteraction.action)
    ).all()
    return {action.value: count for action, count in rows}


# =============================================================================
# Search & Discovery CRUD operations
# =============================================================================


def search_races(
    *,
    session: Session,
    q: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    radius_km: float | None = None,
    distance_min_km: float | None = None,
    distance_max_km: float | None = None,
    terrain: TerrainEnum | None = None,
    difficulty: DifficultyEnum | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    tag_slugs: list[str] | None = None,
    status: RaceStatusEnum | None = None,
    province_code: str | None = None,
    ward_code: str | None = None,
    sort: str = "date",
    skip: int = 0,
    limit: int = 20,
) -> list[Race]:
    """Full-featured search with FTS, geo, and filters."""
    from app.utils import haversine_sql_expr

    statement = select(Race)

    # Full-text search via tsvector
    if q:
        statement = statement.where(
            text("race.search_vector @@ plainto_tsquery('english', :q)").bindparams(q=q)
        )

    # Geo radius filter
    if lat is not None and lon is not None and radius_km is not None:
        dist_expr = haversine_sql_expr(lat, lon)
        statement = statement.where(
            text(f"{dist_expr} <= :radius_km").bindparams(radius_km=radius_km)
        )

    # Category distance filter — race must have at least one category in range
    if distance_min_km is not None or distance_max_km is not None:
        cat_stmt = select(RaceCategory.race_id).where(RaceCategory.race_id == Race.id)
        if distance_min_km is not None:
            cat_stmt = cat_stmt.where(RaceCategory.distance_km >= distance_min_km)
        if distance_max_km is not None:
            cat_stmt = cat_stmt.where(RaceCategory.distance_km <= distance_max_km)
        statement = statement.where(col(Race.id).in_(cat_stmt))

    # Terrain & difficulty
    if terrain is not None:
        statement = statement.where(Race.terrain_type == terrain)
    if difficulty is not None:
        statement = statement.where(Race.difficulty_level == difficulty)

    # Date range
    if date_from is not None:
        statement = statement.where(col(Race.event_start_date) >= date_from)
    if date_to is not None:
        statement = statement.where(col(Race.event_start_date) <= date_to)

    # Tag filter — race must have ALL specified tags
    if tag_slugs:
        for slug in tag_slugs:
            tag_sub = (
                select(RaceTagLink.race_id)
                .join(RaceTag, RaceTagLink.tag_id == RaceTag.id)
                .where(RaceTag.slug == slug)
            )
            statement = statement.where(col(Race.id).in_(tag_sub))

    # Status
    if status is not None:
        statement = statement.where(Race.status == status)

    # Location filters (Vietnamese administrative data)
    if province_code is not None:
        statement = statement.where(Race.province_code == province_code)
    if ward_code is not None:
        statement = statement.where(Race.ward_code == ward_code)

    # Sorting
    if sort == "popularity":
        pop_sub = (
            select(
                UserRaceInteraction.race_id,
                func.count(UserRaceInteraction.id).label("interaction_count"),
            )
            .group_by(UserRaceInteraction.race_id)
            .subquery()
        )
        statement = (
            statement.outerjoin(pop_sub, Race.id == pop_sub.c.race_id)
            .order_by(col(pop_sub.c.interaction_count).desc().nulls_last())
        )
    elif sort == "distance" and lat is not None and lon is not None:
        dist_expr = haversine_sql_expr(lat, lon)
        statement = statement.order_by(text(dist_expr))
    else:
        statement = statement.order_by(col(Race.event_start_date).asc())

    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement).all())


def search_races_count(
    *,
    session: Session,
    q: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    radius_km: float | None = None,
    distance_min_km: float | None = None,
    distance_max_km: float | None = None,
    terrain: TerrainEnum | None = None,
    difficulty: DifficultyEnum | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    tag_slugs: list[str] | None = None,
    status: RaceStatusEnum | None = None,
    province_code: str | None = None,
    ward_code: str | None = None,
) -> int:
    """Count matching races for search (mirrors search_races filters)."""
    from app.utils import haversine_sql_expr

    statement = select(func.count(Race.id))

    if q:
        statement = statement.where(
            text("race.search_vector @@ plainto_tsquery('english', :q)").bindparams(q=q)
        )
    if lat is not None and lon is not None and radius_km is not None:
        dist_expr = haversine_sql_expr(lat, lon)
        statement = statement.where(
            text(f"{dist_expr} <= :radius_km").bindparams(radius_km=radius_km)
        )
    if distance_min_km is not None or distance_max_km is not None:
        cat_stmt = select(RaceCategory.race_id).where(RaceCategory.race_id == Race.id)
        if distance_min_km is not None:
            cat_stmt = cat_stmt.where(RaceCategory.distance_km >= distance_min_km)
        if distance_max_km is not None:
            cat_stmt = cat_stmt.where(RaceCategory.distance_km <= distance_max_km)
        statement = statement.where(col(Race.id).in_(cat_stmt))
    if terrain is not None:
        statement = statement.where(Race.terrain_type == terrain)
    if difficulty is not None:
        statement = statement.where(Race.difficulty_level == difficulty)
    if date_from is not None:
        statement = statement.where(col(Race.event_start_date) >= date_from)
    if date_to is not None:
        statement = statement.where(col(Race.event_start_date) <= date_to)
    if tag_slugs:
        for slug in tag_slugs:
            tag_sub = (
                select(RaceTagLink.race_id)
                .join(RaceTag, RaceTagLink.tag_id == RaceTag.id)
                .where(RaceTag.slug == slug)
            )
            statement = statement.where(col(Race.id).in_(tag_sub))
    if status is not None:
        statement = statement.where(Race.status == status)
    if province_code is not None:
        statement = statement.where(Race.province_code == province_code)
    if ward_code is not None:
        statement = statement.where(Race.ward_code == ward_code)

    return session.exec(statement).one()


def get_races_by_ids(
    *, session: Session, race_ids: list[uuid.UUID]
) -> list[Race]:
    """Fetch races by a list of IDs, preserving order."""
    if not race_ids:
        return []
    rows = list(session.exec(select(Race).where(col(Race.id).in_(race_ids))).all())
    id_to_race = {r.id: r for r in rows}
    return [id_to_race[rid] for rid in race_ids if rid in id_to_race]


def semantic_search_races(
    *,
    session: Session,
    query_embedding: list[float],
    limit: int = 40,
) -> list[tuple[uuid.UUID, int]]:
    """Return (race_id, rank) pairs ordered by cosine similarity to query_embedding.

    Uses pgvector <=> (cosine distance) operator. Returns a ranked list of IDs
    suitable for RRF fusion with FTS results.
    """
    embedding_literal = "[" + ",".join(str(v) for v in query_embedding) + "]"
    sql = text(
        f"SELECT id, ROW_NUMBER() OVER (ORDER BY embedding <=> '{embedding_literal}'::vector) AS rank "
        "FROM race WHERE embedding IS NOT NULL "
        f"LIMIT {limit}"
    )
    rows = session.execute(sql).fetchall()
    return [(row[0], int(row[1])) for row in rows]


def rrf_merge_race_ids(
    fts_ids: list[uuid.UUID],
    vec_ids: list[tuple[uuid.UUID, int]],
    k: int = 60,
    limit: int = 20,
) -> list[uuid.UUID]:
    """Reciprocal Rank Fusion of FTS and vector search results."""
    scores: dict[uuid.UUID, float] = {}
    for rank, race_id in enumerate(fts_ids, start=1):
        scores[race_id] = scores.get(race_id, 0.0) + 1.0 / (k + rank)
    for race_id, rank in vec_ids:
        scores[race_id] = scores.get(race_id, 0.0) + 1.0 / (k + rank)
    sorted_ids = sorted(scores.keys(), key=lambda rid: scores[rid], reverse=True)
    return sorted_ids[:limit]


def get_nearby_races(
    *,
    session: Session,
    lat: float,
    lon: float,
    radius_km: float = 100.0,
    limit: int = 20,
) -> list[tuple[Race, float]]:
    """Return (race, distance_km) tuples sorted by distance ascending."""
    from app.utils import haversine_distance_km, haversine_sql_expr

    dist_expr = haversine_sql_expr(lat, lon)
    statement = (
        select(Race)
        .where(Race.latitude.isnot(None))  # type: ignore[union-attr]
        .where(Race.longitude.isnot(None))  # type: ignore[union-attr]
        .where(text(f"{dist_expr} <= :radius_km").bindparams(radius_km=radius_km))
        .order_by(text(dist_expr))
        .limit(limit)
    )
    races = list(session.exec(statement).all())
    return [
        (race, haversine_distance_km(lat, lon, race.latitude, race.longitude))  # type: ignore[arg-type]
        for race in races
    ]


def get_trending_races(
    *,
    session: Session,
    days: int = 7,
    limit: int = 10,
) -> list[Race]:
    """Return races ranked by interaction count in the last N days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    pop_sub = (
        select(
            UserRaceInteraction.race_id,
            func.count(UserRaceInteraction.id).label("cnt"),
        )
        .where(col(UserRaceInteraction.created_at) >= cutoff)
        .group_by(UserRaceInteraction.race_id)
        .subquery()
    )
    statement = (
        select(Race)
        .outerjoin(pop_sub, Race.id == pop_sub.c.race_id)
        .order_by(col(pop_sub.c.cnt).desc().nulls_last())
        .limit(limit)
    )
    return list(session.exec(statement).all())


def get_similar_races(
    *,
    session: Session,
    race: Race,
    limit: int = 6,
) -> list[Race]:
    """Return races similar to the given race by terrain, difficulty, and region."""
    statement = select(Race).where(Race.id != race.id)

    filters = []
    if race.terrain_type is not None:
        filters.append(Race.terrain_type == race.terrain_type)
    if race.difficulty_level is not None:
        filters.append(Race.difficulty_level == race.difficulty_level)
    if race.country:
        filters.append(Race.country == race.country)

    if filters:
        statement = statement.where(or_(*filters))

    statement = statement.order_by(col(Race.event_start_date).asc()).limit(limit)
    return list(session.exec(statement).all())


def get_recommended_races(
    *,
    session: Session,
    user_id: uuid.UUID,
    limit: int = 10,
) -> list[Race]:
    """
    Return personalized race recommendations.
    Falls back to trending if user has no profile or sparse preferences.
    """
    profile = get_user_profile(session=session, user_id=user_id)

    if profile is None:
        return get_trending_races(session=session, limit=limit)

    statement = select(Race)
    filters = []

    if profile.terrain_preference is not None:
        filters.append(Race.terrain_type == profile.terrain_preference)

    if profile.distance_preference is not None:
        dist_ranges: dict[str, tuple[float, float]] = {
            DistancePrefEnum.SHORT.value: (0, 10),
            DistancePrefEnum.MID.value: (10, 30),
            DistancePrefEnum.LONG.value: (30, 60),
            DistancePrefEnum.ULTRA.value: (60, 9999),
        }
        range_key = profile.distance_preference.value if hasattr(profile.distance_preference, "value") else str(profile.distance_preference)
        if range_key in dist_ranges:
            lo, hi = dist_ranges[range_key]
            cat_sub = (
                select(RaceCategory.race_id)
                .where(RaceCategory.distance_km >= lo, RaceCategory.distance_km <= hi)
            )
            filters.append(col(Race.id).in_(cat_sub))

    if filters:
        statement = statement.where(or_(*filters))

    # Exclude already-saved races
    saved_ids = (
        select(UserRaceInteraction.race_id)
        .where(
            UserRaceInteraction.user_id == user_id,
            UserRaceInteraction.action == InteractionTypeEnum.SAVED,
        )
    )
    statement = statement.where(col(Race.id).notin_(saved_ids))

    statement = statement.order_by(col(Race.event_start_date).asc()).limit(limit)
    results = list(session.exec(statement).all())

    # Pad with trending if not enough results
    if len(results) < limit:
        existing_ids = {r.id for r in results}
        trending = get_trending_races(session=session, limit=limit)
        for r in trending:
            if r.id not in existing_ids:
                results.append(r)
                existing_ids.add(r.id)
            if len(results) >= limit:
                break

    return results
