import uuid

from sqlmodel import Session, func, select

from app.models import Item, ItemCreate, ItemUpdate


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    """
    Create a new item.

    Creates a new Item object and associates it with an owner.

    Args:
        session: The database session.
        item_in: The ItemCreate object containing item information.
        owner_id: The UUID of the user who owns this item.

    Returns:
        The newly created Item object.

    Raises:
        SQLAlchemyError: If there's an error during database operations.

    Notes:
        This function is not protected and can be called by any authenticated user.
    """
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def get_item(*, session: Session, item_id: uuid.UUID) -> Item | None:
    """
    Get an item by ID.

    Retrieves an item from the database by its UUID.

    Args:
        session: The database session.
        item_id: The UUID of the item to retrieve.

    Returns:
        The Item object if found, None otherwise.

    Notes:
        This function is not protected and can be called by any authenticated user.
    """
    return session.get(Item, item_id)


def get_items(*, session: Session, skip: int = 0, limit: int = 100) -> list[Item]:
    """
    Get a list of items.

    Retrieves a list of items from the database with pagination.

    Args:
        session: The database session.
        skip: The number of items to skip (for pagination).
        limit: The maximum number of items to return (for pagination).

    Returns:
        A list of Item objects.

    Notes:
        This function is not protected and can be called by any authenticated user.
    """
    statement = select(Item).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_items_by_owner(
    *, session: Session, owner_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[Item]:
    """
    Get items by owner.

    Retrieves a list of items from the database for a specific owner with pagination.

    Args:
        session: The database session.
        owner_id: The UUID of the owner.
        skip: The number of items to skip (for pagination).
        limit: The maximum number of items to return (for pagination).

    Returns:
        A list of Item objects owned by the specified user.

    Notes:
        This function is not protected and can be called by any authenticated user.
    """
    statement = select(Item).where(Item.owner_id == owner_id).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_item_count(*, session: Session) -> int:
    """
    Get the total number of items.

    Counts the total number of items in the database.

    Args:
        session: The database session.

    Returns:
        The total number of items as an integer.

    Notes:
        This function is not protected and can be called by any authenticated user.
    """
    return session.exec(select(func.count()).select_from(Item)).one()


def get_item_count_by_owner(*, session: Session, owner_id: uuid.UUID) -> int:
    """
    Get the number of items by owner.

    Counts the number of items in the database for a specific owner.

    Args:
        session: The database session.
        owner_id: The UUID of the owner.

    Returns:
        The number of items owned by the specified user as an integer.

    Notes:
        This function is not protected and can be called by any authenticated user.
    """
    return session.exec(
        select(func.count()).where(Item.owner_id == owner_id).select_from(Item)
    ).one()


def update_item(*, session: Session, db_item: Item, item_in: ItemUpdate) -> Item:
    """
    Update an item.

    Updates the attributes of an item in the database.

    Args:
        session: The database session.
        db_item: The Item object to update.
        item_in: The ItemUpdate object containing the new attribute values.

    Returns:
        The updated Item object.

    Raises:
        SQLAlchemyError: If there's an error during database operations.

    Notes:
        This function is not protected and can be called by any authenticated user.
    """
    item_data = item_in.model_dump(exclude_unset=True)
    db_item.sqlmodel_update(item_data)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def delete_item(*, session: Session, item_id: uuid.UUID) -> Item | None:
    """
    Delete an item.

    Deletes an item from the database by its UUID.

    Args:
        session: The database session.
        item_id: The UUID of the item to delete.

    Returns:
        The deleted Item object if found and deleted, None otherwise.

    Raises:
        SQLAlchemyError: If there's an error during database operations.

    Notes:
        This function is not protected and can be called by any authenticated user.
    """
    item = session.get(Item, item_id)
    if item:
        session.delete(item)
        session.commit()
    return item
