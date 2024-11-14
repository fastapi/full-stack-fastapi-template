# This script is a set of utility functions that manage user and item creation, updates, and authentication within a FastAPI application using SQLModel.
# Each function interacts with the database through a Session object, performing standard CRUD operations and handling security concerns like password hashing and verification.
# Database interaction functions (CRUD operations) for data. CRUD stands for Create, Read, Update, and Delete
import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate

# create_user: Creates a new user in the database, hashing the user's password before saving it.

def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

# update_user: Updates an existing user's information in the database, including re-hashing the password if it’s updated.

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

# get_user_by_email: Retrieves a user from the database based on their email address.

def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user

# authenticate: Authenticates a user by verifying their email and password, returning the user if the credentials match.

def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user

# create_item: Creates a new item in the database, associating it with the owner (a specific user).

def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

from app.models import GeoFile  # Import the GeoFile model

# create_geofile: Adds a new GeoFile record to the database.

def create_geofile(session: Session, file_name: str, file_path: str, description: str = None) -> GeoFile:
    geofile = GeoFile(file_name=file_name, file_path=file_path, description=description)
    session.add(geofile)       # Add the new GeoFile instance to the session.
    session.commit()            # Commit the transaction to save the GeoFile in the database.
    session.refresh(geofile)    # Refresh the instance to load any updated database state.
    return geofile              # Return the created GeoFile object.

# get_geofile: Retrieves a GeoFile record by its unique ID.

def get_geofile(session: Session, geofile_id: uuid.UUID) -> GeoFile | None:
    return session.get(GeoFile, geofile_id)  # Get the GeoFile by its ID, or None if not found.

# list_geofiles: Retrieves all GeoFile records from the database.

def list_geofiles(session: Session) -> list[GeoFile]:
    statement = select(GeoFile)                  # Prepare a query to select all GeoFile records.
    return session.exec(statement).all()         # Execute the query and return all results as a list.