import datetime
import uuid
from fastapi import HTTPException
from sqlmodel import SQLModel, Session, select
from typing import List, Type

# Generic CRUD function to get all records with pagination
def get_all_records(
    session: Session, model: Type[SQLModel], skip: int = 0, limit: int = 10
) -> List[SQLModel]:
    """
    Retrieve a paginated list of records.
    - **session**: Database session
    - **model**: SQLModel class (e.g., Nightclub, Restaurant, QSR, Foodcourt)
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    """
    try:
        statement = select(model).offset(skip).limit(limit)
        result = session.execute(statement).scalars().all()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving {model.__name__} records: {str(e)}")

# Function to get a single record by ID
def get_record_by_id(
    session: Session, model: Type[SQLModel], record_id: uuid.UUID
) -> SQLModel:
    """
    Retrieve a single record by ID.
    - **session**: Database session
    - **model**: SQLModel class (e.g., Nightclub, Restaurant, QSR, Foodcourt)
    - **record_id**: ID of the record to retrieve
    """
    try:
        statement = select(model).where(model.id == record_id)
        result = session.execute(statement).scalars().first()
        if not result:
            raise HTTPException(status_code=404, detail=f"{model.__name__} with ID {record_id} not found.")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving {model.__name__} record: {str(e)}")

# Function to create a new record
# Create a new record
def create_record(
    session: Session, model: Type[SQLModel], obj_in: SQLModel
) -> SQLModel:
    """
    Create a new record with automatic `created_at` and `updated_at` timestamps.
    - **session**: Database session
    - **model**: SQLModel class (e.g., Nightclub, Restaurant, QSR, Foodcourt)
    - **obj_in**: Data to create the new record
    """
    try:
        # Prepare the data for creation
        obj_data = obj_in.model_dump()
        
        # Set `created_at` and `updated_at` timestamps
        obj_data['created_at'] = datetime.utcnow()
        obj_data['updated_at'] = datetime.utcnow()
        
        # Create the new object
        obj = model(**obj_data)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating {model.__name__}: {str(e)}")


# Update an existing record
def update_record(
    session: Session, model: Type[SQLModel], record_id: uuid.UUID, obj_in: SQLModel
) -> SQLModel:
    """
    Update an existing record with automatic `updated_at` timestamp.
    - **session**: Database session
    - **model**: SQLModel class (e.g., Nightclub, Restaurant, QSR, Foodcourt)
    - **record_id**: ID of the record to update
    - **obj_in**: Data to update the record
    """
    try:
        # Retrieve the existing record
        obj = get_record_by_id(session, model, record_id)
        
        # Convert incoming data
        obj_data = obj_in.model_dump()
        
        # Update the fields
        for field, value in obj_data.items():
            setattr(obj, field, value)
        
        # Set `updated_at` to the current time
        obj.updated_at = datetime.utcnow()
        
        # Commit the changes
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating {model.__name__}: {str(e)}")


# Partially update an existing record
def patch_record(
    session: Session, model: Type[SQLModel], record_id: uuid.UUID, obj_in: SQLModel
) -> SQLModel:
    """
    Partially update an existing record with automatic `updated_at` timestamp.
    - **session**: Database session
    - **model**: SQLModel class (e.g., Nightclub, Restaurant, QSR)
    - **record_id**: ID of the record to update
    - **obj_in**: Partial data to update the record
    """
    try:
        # Get the existing record from the database
        obj = get_record_by_id(session, model, record_id)

        # Convert the incoming data
        obj_data = obj_in.model_dump()
        
        # Update the fields on the object
        for field, value in obj_data.items():
            setattr(obj, field, value)
        
        # Set `updated_at` to the current time
        obj.updated_at = datetime.utcnow()
        
        # Commit the changes
        session.add(obj)
        session.commit()
        session.refresh(obj)
        
        return obj
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating {model.__name__}: {str(e)}")
    
# Function to delete a record
def delete_record(
    session: Session, model: Type[SQLModel], record_id: uuid.UUID
) -> None:
    """
    Delete a record by ID.
    - **session**: Database session
    - **model**: SQLModel class (e.g., Nightclub, Restaurant, QSR, Foodcourt)
    - **record_id**: ID of the record to delete
    """
    try:
        obj = get_record_by_id(session, model, record_id)
        session.delete(obj)
        session.commit()
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting {model.__name__} with ID {record_id}: {str(e)}")