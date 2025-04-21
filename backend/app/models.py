from typing import Optional
import uuid

from pydantic import EmailStr, BaseModel
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
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

class TaskDifficulty(enum.Enum):
    ONE_STAR = "one_star"
    TWO_STAR = "two_star"
    THREE_STAR = "three_star"
    FOUR_STAR = "four_star"
    FIVE_STAR = "five_star"


class Task(SQLModel, table=True):
    __tablename__ = "tasks" 

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    title: str = Field(..., max_length=255, description="Заголовок задачи (короткое описание)")
    description: str = Field(..., description="Полный текст задачи (условие)")
    test_cases: str = Field(..., description="JSON-объект с тестами (входные данные и ожидание ответа)")
    constraints: str = Field(default=None, description="JSON-объект с ограничениями (например, время/память)")
    difficulty: TaskDifficulty = Field(default=TaskDifficulty.ONE_STAR, description="Сложность задачи (1-5 звезд)")
    tags: str = Field(default=None, description="Тема задачи или теги (например, ['dynamic programming', 'math'])")
    illumination_type: str = Field(default=None, description="Тип иллюминации, к которой относится задача (interview, kids)")
    category: str = Field(description="Категория задачи (строки, числа, связные списки и пр.)")
    hint: Optional[str] = Field(default=None, description="Подсказка к задаче")
    created_at: datetime = Field(default_factory=datetime, description="Дата создания задачи")
    is_active: bool = Field(default=True, description="Активность задачи (например, скрытие её в системе)")
    solutions: list["Solution"] = Relationship(back_populates="task")


class Solution(SQLModel, table=True):
    __tablename__ = "solutions"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    task_id: int = Field(..., foreign_key="tasks.id", description="Связь с задачей")
    solution_code: str = Field(..., description="Текст решения (например, Python-код)")
    is_correct: bool = Field(default=False, description="Флаг корректности решения")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Дата создания решения")
    task: Task = Relationship(back_populates="solutions")

class TaskPublic(BaseModel):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    title: str = Field(..., max_length=255, description="Заголовок задачи (короткое описание)")
    description: str = Field(..., description="Полный текст задачи (условие)")
    difficulty: TaskDifficulty = Field(default=TaskDifficulty.ONE_STAR, description="Сложность задачи (1-5 звезд)")
    illumination_type: str = Field(default=None, description="Тип иллюминации, к которой относится задача (interview, kids)")
    category: str = Field(description="Категория задачи (строки, числа, связные списки и пр.)")
    created_at: datetime = Field(default_factory=datetime, description="Дата создания задачи")

class IlluminationPublic(SQLModel):
    illumination_type: str
    tasks: list[TaskPublic]

