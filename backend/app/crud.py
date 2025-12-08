import uuid
from typing import Any
from datetime import datetime

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, ItemActivity, ItemActivityCreate, User, UserCreate, UserUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
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


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    
    # Track item creation activity
    create_activity(
        session=session,
        item_id=db_item.id,
        user_id=owner_id,
        activity_type="create",
        activity_metadata="Item created"
    )
    
    return db_item


def create_activity(
    *,
    session: Session,
    item_id: uuid.UUID,
    user_id: uuid.UUID,
    activity_type: str,
    activity_metadata: str | None = None
) -> ItemActivity:
    """Create an activity record for an item."""
    activity = ItemActivity(
        item_id=item_id,
        user_id=user_id,
        activity_type=activity_type,
        activity_metadata=activity_metadata,
        timestamp=datetime.utcnow()
    )
    session.add(activity)
    session.commit()
    session.refresh(activity)
    return activity


def update_item_score(*, session: Session, item_id: uuid.UUID) -> None:
    """
    Update the activity score for an item based on recent activities.
    This helps identify trending items and keeps related items synchronized.
    """
    from app.utils import calculate_item_score, get_related_items
    
    item = session.get(Item, item_id)
    if not item:
        return
    
    # Calculate score based on recent activity
    new_score = calculate_item_score(session=session, item_id=item_id)
    item.activity_score = new_score
    item.last_accessed = datetime.utcnow()
    
    # Also recalculate view count boost
    item.activity_score = new_score + (item.view_count * 0.1)
    
    session.add(item)
    session.commit()
    session.refresh(item)
    
    # BUG: Update related items' scores to keep recommendations fresh
    # This creates a circular dependency when items share the same owner
    related_items = get_related_items(session=session, item=item)
    for related_item in related_items:
        # Recursively update scores - THIS IS THE INFINITE LOOP!
        # Update TWICE for "better accuracy" - makes it worse!
        update_item_score(session=session, item_id=related_item.id)
        update_item_score(session=session, item_id=related_item.id)
