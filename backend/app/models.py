import uuid
from datetime import date, datetime, timezone

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


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
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Shared properties for Company (PJ)
class CompanyBase(SQLModel):
    cnpj: str = Field(min_length=1, max_length=20)
    razao_social: str = Field(min_length=1, max_length=255)
    representante_legal: str = Field(min_length=1, max_length=255)
    data_abertura: date
    nome_fantasia: str = Field(min_length=1, max_length=255)
    porte: str = Field(min_length=1, max_length=100)
    atividade_economica_principal: str = Field(min_length=1, max_length=255)
    atividade_economica_secundaria: str = Field(min_length=1, max_length=255)
    natureza_juridica: str = Field(min_length=1, max_length=255)
    logradouro: str = Field(min_length=1, max_length=255)
    numero: str = Field(min_length=1, max_length=20)
    complemento: str = Field(min_length=1, max_length=255)
    cep: str = Field(min_length=1, max_length=10)
    bairro: str = Field(min_length=1, max_length=255)
    municipio: str = Field(min_length=1, max_length=255)
    uf: str = Field(min_length=1, max_length=2)
    endereco_eletronico: str = Field(min_length=1, max_length=255)
    telefone_comercial: str = Field(min_length=1, max_length=20)
    situacao_cadastral: str = Field(min_length=1, max_length=100)
    data_situacao_cadastral: date
    cpf_representante_legal: str = Field(min_length=1, max_length=14)
    identidade_representante_legal: str = Field(min_length=1, max_length=20)
    logradouro_representante_legal: str = Field(min_length=1, max_length=255)
    numero_representante_legal: str = Field(min_length=1, max_length=20)
    complemento_representante_legal: str = Field(min_length=1, max_length=255)
    cep_representante_legal: str = Field(min_length=1, max_length=10)
    bairro_representante_legal: str = Field(min_length=1, max_length=255)
    municipio_representante_legal: str = Field(min_length=1, max_length=255)
    uf_representante_legal: str = Field(min_length=1, max_length=2)
    endereco_eletronico_representante_legal: str = Field(min_length=1, max_length=255)
    telefones_representante_legal: str = Field(min_length=1, max_length=40)
    data_nascimento_representante_legal: date
    banco_cc_cnpj: str = Field(min_length=1, max_length=100)
    agencia_cc_cnpj: str = Field(min_length=1, max_length=20)


# Properties to receive on company creation
class CompanyCreate(CompanyBase):
    pass


# Database model, database table inferred from class name
class Company(CompanyBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    cnpj: str = Field(unique=True, index=True, min_length=1, max_length=20)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


# Properties to return via API, id is always required
class CompanyPublic(CompanyBase):
    id: uuid.UUID
    created_at: datetime | None = None


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
    new_password: str = Field(min_length=8, max_length=128)
