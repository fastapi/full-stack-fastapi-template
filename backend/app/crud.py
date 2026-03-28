import uuid
from datetime import datetime, timezone
from typing import Any

from sqlmodel import Session, col, func, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    ItemCreate,
    MediaAsset,
    MediaAssetCreate,
    MediaAssetUpdate,
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
    RaceUpdate,
    Role,
    RoleCreate,
    User,
    UserCreate,
    UserUpdate,
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
    db_race = Race.model_validate(race_in, update={"organizer_id": organizer_id})
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
    race_data["updated_at"] = datetime.now(timezone.utc)
    db_race.sqlmodel_update(race_data)
    session.add(db_race)
    session.commit()
    session.refresh(db_race)
    return db_race


def delete_race(*, session: Session, race_id: uuid.UUID) -> bool:
    """Delete a race."""
    race = session.get(Race, race_id)
    if race:
        session.delete(race)
        session.commit()
        return True
    return False


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
