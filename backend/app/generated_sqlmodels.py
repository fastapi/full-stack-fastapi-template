import uuid

from sqlalchemy import Boolean, Column, ForeignKeyConstraint, Index, PrimaryKeyConstraint, String, Uuid
from sqlmodel import Field, Relationship, SQLModel

class Category(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id', name='category_pkey'),
    )

    name: str = Field(sa_column=Column('name', String(100), nullable=False))
    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True))
    created_at: str = Field(sa_column=Column('created_at', String, nullable=False))
    description: str | None = Field(default=None, sa_column=Column('description', String(500)))


class User(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id', name='user_pkey'),
        Index('ix_user_email', 'email', unique=True)
    )

    email: str = Field(sa_column=Column('email', String(255), nullable=False))
    is_active: bool = Field(sa_column=Column('is_active', Boolean, nullable=False))
    is_superuser: bool = Field(sa_column=Column('is_superuser', Boolean, nullable=False))
    hashed_password: str = Field(sa_column=Column('hashed_password', String, nullable=False))
    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True))
    full_name: str | None = Field(default=None, sa_column=Column('full_name', String(255)))

    item: list['Item'] = Relationship(back_populates='owner')


class Item(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['owner_id'], ['user.id'], ondelete='CASCADE', name='item_owner_id_fkey'),
        PrimaryKeyConstraint('id', name='item_pkey')
    )

    title: str = Field(sa_column=Column('title', String(255), nullable=False))
    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True))
    owner_id: uuid.UUID = Field(sa_column=Column('owner_id', Uuid, nullable=False))
    description: str | None = Field(default=None, sa_column=Column('description', String(255)))

    owner: 'User' | None = Relationship(back_populates='item')
