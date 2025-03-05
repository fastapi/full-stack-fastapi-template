import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic import Field as F
from sqlmodel import Field, Relationship, SQLModel, Column, TIMESTAMP, text, DATE
from datetime import datetime
from sqlalchemy import JSON
from sqlalchemy import Column as Col
import enum
# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    Patients: list["Patient"] = Relationship(back_populates="owner", cascade_delete=True)

# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


################################################################################
##                                 Start Here!                                ##
################################################################################

# Shared properties
class PatientBase(SQLModel):
    full_name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    email: EmailStr = Field(max_length=55)
    phone_number: str = Field(max_length=20)
    height: float = Field(max_length=20)
    weight: float = Field(max_length=20)
    gender: int = Field(max_length=20)
    birth_date: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False, 
    ))
 


# Properties to receive on item creation
class PatientCreate(PatientBase):
    pass


# Properties to receive on item update
class PatientUpdate(PatientBase):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore
    description: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(max_length=55)
    phone_number: str | None  = Field(max_length=20)
    height: float | None = Field(max_length=20)
    weight: float | None = Field(max_length=20)
    gender: int | None = Field(max_length=20)

# Database model, database table inferred from class name
class Patient(PatientBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="Patients")
    created_datetime: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    menus: list["Menu"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class PatientPublic(PatientBase):
    pass


class PatientsPublic(SQLModel):
    data: list[PatientPublic]
    count: int

class Menu_B(BaseModel):
    def __init__(self):
        self.data: dict = F(default=self.menu_builder())

    def menu_builder(self):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday" , "Sunday"]
        mills = ["breakfast",  "mid-morning", "lunch","mid-afternoon" , "dinner"]
        new_menu = {}
        for day in days:
            new_menu.update({day:{mill:{} for mill in mills}})
        self.data = new_menu 
        return self.data

# Shared properties
class MenuBase(SQLModel,Menu_B):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    data: dict = Field(sa_column=Col(JSON), default_factory=dict)
    current: bool = Field()


# Properties to receive on item creation
class MenuCreate(MenuBase):
    pass


# Properties to receive on item update
class MenuUpdate(MenuBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore
    description: str | None = Field(default=None, max_length=255)
    data: dict = Field(sa_column=Column(JSON), default_factory=dict)
    current: bool = Field()

# Database model, database table inferred from class name
class Menu(MenuBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    created_datetime: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    owner_id: uuid.UUID = Field(
        foreign_key="patient.id", nullable=False, ondelete="CASCADE"
    )
    owner: Patient | None = Relationship(back_populates="menus")


# Properties to return via API, id is always required
class MenuPublic(MenuBase):
    pass


class MenusPublic(SQLModel):
    data: list[MenuPublic]
    count: int

