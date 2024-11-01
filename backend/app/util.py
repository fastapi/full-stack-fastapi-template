import logging
import uuid
from typing import TypeVar

from fastapi import HTTPException
from pydantic import BaseModel
from sqlmodel import Session, SQLModel, select

from app.models.user import UserBusiness, UserVenueAssociation

# Generic CRUD function to get all records with pagination
T = TypeVar("T", bound=SQLModel)


def get_all_records(
    session: Session, model: type[T], skip: int = 0, limit: int = 10
) -> list[SQLModel]:
    """
    Retrieve a paginated list of records as schemas.
    - **session**: Database session
    - **model**: SQLModel class (e.g., Nightclub, Restaurant, QSR, Foodcourt)
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    """

    try:
        # Fetch raw model instances
        statement = select(model).offset(skip).limit(limit)
        result = session.execute(statement).scalars().all()

        # Convert each record to its read schema
        return result
    except ValueError as ve:
        # Handle errors (optional, add specific error handling as needed)
        print(f"Error fetching records: {ve}")
        return []


def get_record_by_id(db: Session, model: type[T], record_id: uuid.UUID) -> T | None:
    """
    Generic function to retrieve a record by its ID.

    Args:
        db (Session): The database session.
        model (Type[T]): The SQLModel class representing the table.
        record_id (uuid.UUID): The ID of the record to retrieve.

    Returns:
        Optional[T]: The retrieved record if found, otherwise None.

    Raises:
        HTTPException: If the record is not found, raises a 404 error.
    """
    record = db.get(model, record_id)
    if not record:
        raise HTTPException(
            status_code=404, detail=f"{model.__name__} with ID {record_id} not found."
        )
    return record


# Function to create a new record
# Create a new record
def create_record(db: Session, instance: SQLModel) -> SQLModel:
    """
    Create a new record in the database with automatic timestamp management.

    :param db: The active database session.
    :param model: The SQLModel class representing the database model.
    :param instance: An instance of the model to be persisted.
    :return: The created instance with updated attributes.
    """
    # Current UTC time for timestamping
    # current_time = datetime.now()

    # # Setting timestamps for the record
    # instance.created_at = current_time
    # instance.updated_at = current_time

    # Persisting the new record in the database
    db.add(instance)
    db.commit()  # Commit the changes
    db.refresh(instance)  # Refresh to load any generated attributes

    return instance  # Return the created instance


def update_record(db: Session, instance: SQLModel, update_data: BaseModel) -> SQLModel:
    """
    Update an existing record in the database, applying only the changes provided by a Pydantic model.
    This approach ensures validation of input data and prevents partial updates with invalid fields.

    :param db: Active database session.
    :param instance: Existing model instance to be updated.
    :param update_data: Pydantic model containing the fields to update.
    :return: The updated model instance with changes committed.
    """
    try:
        # Convert the Pydantic model to a dictionary, excluding unset fields
        update_dict = update_data.dict(exclude_unset=True)

        # Apply updates to only the fields that are set in the update_data Pydantic model
        for key, value in update_dict.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
            else:
                raise ValueError(f"Field '{key}' does not exist on the model.")

        # Persist the changes in a single transaction
        db.add(instance)
        db.commit()
        db.refresh(instance)

        return instance

    except ValueError as ve:
        logging.error("Validation error: %s", ve)
        db.rollback()  # Undo any changes in case of failure
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        logging.error("Unexpected error during record update: %s", e)
        db.rollback()  # Rollback any transaction in case of failure
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while updating the record.",
        ) from e


# Function to delete a record
def delete_record(db: Session, instance: SQLModel) -> None:
    """
    Delete a record from the database.

    :param db: The active database session.
    :param instance: The instance of the model to be deleted.
    :return: None
    """
    db.delete(instance)
    db.commit()


def check_user_permission(db: Session, current_user: UserBusiness, venue_id: uuid.UUID):
    """
    Check if the user has permission to manage the specified venue.

    Args:
        db: Database session.
        current_user: The current user object.
        venue_id: The ID of the venue to check permissions for.

    Raises:
        HTTPException: If the user does not have permission.

    Returns:
        UserVenueAssociation: The association record if it exists.
    """
    statement = select(UserVenueAssociation).where(
        UserVenueAssociation.user_id == current_user.id,
        UserVenueAssociation.venue_id == venue_id,
    )

    user_venue_association = db.execute(statement).scalars().first()

    if user_venue_association is None:
        raise HTTPException(
            status_code=403,
            detail="User does not have permission to manage this venue.",
        )

    return user_venue_association
