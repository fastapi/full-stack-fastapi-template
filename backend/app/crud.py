from http.client import HTTPException
import uuid
from typing import Any

from app.models.venue import QSR, Foodcourt, Nightclub, Restaurant
# from app.models.user import UserBusiness, UserPublic

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password


from typing import Type, List
from sqlmodel import select, Session, SQLModel

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
    statement = select(model).offset(skip).limit(limit)
    result = session.exec(statement)
    return result.all()

# Function to get a single record by ID
def get_record_by_id(
    session: Session, model: Type[SQLModel], record_id: int
) -> SQLModel:
    """
    Retrieve a single record by ID.
    - **session**: Database session
    - **model**: SQLModel class (e.g., Nightclub, Restaurant, QSR, Foodcourt)
    - **record_id**: ID of the record to retrieve
    """
    statement = select(model).where(model.id == record_id)
    result = session.exec(statement).first()
    if not result:
        raise ValueError(f"{model.__name__} with ID {record_id} not found.")
    return result

# Function to create a new record
def create_record(
    session: Session, model: Type[SQLModel], obj_in: SQLModel
) -> SQLModel:
    """
    Create a new record.
    - **session**: Database session
    - **model**: SQLModel class (e.g., Nightclub, Restaurant, QSR, Foodcourt)
    - **obj_in**: Data to create the new record
    """
    obj = model(**obj_in.dict())
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj

# Function to update an existing record
def update_record(
    session: Session, model: Type[SQLModel], record_id: int, obj_in: SQLModel
) -> SQLModel:
    """
    Update an existing record.
    - **session**: Database session
    - **model**: SQLModel class (e.g., Nightclub, Restaurant, QSR, Foodcourt)
    - **record_id**: ID of the record to update
    - **obj_in**: Data to update the record
    """
    obj = get_record_by_id(session, model, record_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Record not found")
    obj_data = obj_in.dict(exclude_unset=True)
    for field, value in obj_data.items():
        setattr(obj, field, value)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj

# Function to delete a record
def delete_record(
    session: Session, model: Type[SQLModel], record_id: int
) -> None:
    """
    Delete a record by ID.
    - **session**: Database session
    - **model**: SQLModel class (e.g., Nightclub, Restaurant, QSR, Foodcourt)
    - **record_id**: ID of the record to delete
    """
    obj = get_record_by_id(session, model, record_id)
    session.delete(obj)
    session.commit()

# Example functions specific to Nightclub, Restaurant, QSR, and Foodcourt

def get_all_nightclubs(
    session: Session, skip: int = 0, limit: int = 10
) -> List[SQLModel]:
    return get_all_records(session, Nightclub, skip, limit)

def get_all_restaurants(
    session: Session, skip: int = 0, limit: int = 10
) -> List[SQLModel]:
    return get_all_records(session, Restaurant, skip, limit)

def get_all_qsrs(
    session: Session, skip: int = 0, limit: int = 10
) -> List[SQLModel]:
    return get_all_records(session, QSR, skip, limit)

def get_all_foodcourts(
    session: Session, skip: int = 0, limit: int = 10
) -> List[SQLModel]:
    return get_all_records(session, Foodcourt, skip, limit)



# def authenticate(*, session: Session, email: str, password: str) -> User | None:
#     db_user = get_user_by_email(session=session, email=email)
#     if not db_user:
#         return None
#     if not verify_password(password, db_user.hashed_password):
#         return None
#     return db_user


# def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
#     db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
#     session.add(db_item)
#     session.commit()
#     session.refresh(db_item)
#     return db_item
