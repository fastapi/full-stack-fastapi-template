import uuid
from datetime import datetime
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

# Define a new database model called GeoFile, which will create a table in the database
class GeoFile(SQLModel, table=True):
    # Unique identifier for each record, generated using UUIDs
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # The name of the file as it was uploaded
    file_name: str = Field(max_length=255)
    
    # The date and time when the file was uploaded, set to the current time by default
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Path where the file is stored on the server
    file_path: str = Field(max_length=255)
    
    # Optional field for a description of the file, with a maximum length of 500 characters
    description: str | None = Field(default=None, max_length=500)

# UserBase: A base class that defines shared properties for the User model.
# It includes fields like email, full_name, is_active, and is_superuser.
# This class is used as a base for other models related to users.
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# UserCreate: Inherits from UserBase and adds a password field.
# This model is used when creating a new user via the API.
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


# UserRegister: Similar to UserCreate but used specifically for user registration.
# Includes fields for email, password, and optional full_name.
class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# UserUpdate: Used for updating existing user details.
# It allows partial updates by making all fields optional.
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


# UserUpdateMe: A model for updating the current user's details.
# It allows users to update their own email and full name.
class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


# UpdatePassword: A model for updating a user's password.
# It includes fields for the current and new passwords.
class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# User: Represents the User table in the database.
# Inherits from UserBase and adds fields for id, hashed_password, and relationships.
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# UserPublic: A model for returning public user data via the API.
# It excludes sensitive information like the hashed password.
class UserPublic(UserBase):
    id: uuid.UUID


# UsersPublic: A model for returning a list of public user data.
# It includes the user data and a count of how many users are returned.
class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# ItemBase: A base class that defines shared properties for the Item model.
# It includes fields like title and description, which are used in other item-related models.
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# ItemCreate: Inherits from ItemBase and is used when creating a new item.
# It allows the creation of an item with the basic fields defined in ItemBase.
class ItemCreate(ItemBase):
    pass


# ItemUpdate: Used for updating an existing item.
# It allows partial updates by making all fields optional.
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Item: Represents the Item table in the database.
# Inherits from ItemBase and adds fields for id, owner_id, and relationships.
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# ItemPublic: A model for returning public item data via the API.
# It includes the item's id and owner_id but excludes sensitive information.
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


# ItemsPublic: A model for returning a list of public item data.
# It includes the item data and a count of how many items are returned.
class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Message: A generic model used to return simple messages via the API.
# Useful for operations that need to return a success or error message.
class Message(SQLModel):
    message: str


# Token: A model used to return an access token as a JSON payload.
# Includes the access token and its type (typically "bearer").
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# TokenPayload: Represents the contents of a JWT token.
# It is used internally to decode and validate tokens.
class TokenPayload(SQLModel):
    sub: str | None = None


# NewPassword: A model for handling password reset requests.
# Includes the reset token and the new password.
class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)