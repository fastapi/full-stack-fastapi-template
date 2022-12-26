from __future__ import annotations
from pydantic import BaseModel, Field, validator, constr
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
import json

from app.schema_types import BaseEnum


class BaseSchema(BaseModel):
    @property
    def as_db_dict(self):
        to_db = self.dict(exclude_defaults=True, exclude_none=True, exclude={"identifier, id"})
        for key in ["id", "identifier"]:
            if key in self.dict().keys():
                to_db[key] = self.dict()[key].hex
        return to_db

    @property
    def as_neo_dict(self):
        to_db = self.json(exclude_defaults=True, exclude_none=True, exclude={"identifier, id"})
        to_db = json.loads(to_db)
        self_dict = self.dict()
        for key in self_dict.keys():
            if isinstance(self_dict[key], BaseEnum):
                # Uppercase the Enum values
                to_db[key] = to_db[key].upper()
            if isinstance(self_dict[key], datetime):
                to_db[key] = datetime.fromisoformat(to_db[key])
            if isinstance(self_dict[key], date):
                to_db[key] = date.fromisoformat(to_db[key])
            if key in ["id", "identifier"]:
                to_db[key] = self_dict[key].hex
        return to_db


class MetadataBaseSchema(BaseSchema):
    # Receive via API
    # https://www.dublincore.org/specifications/dublin-core/dcmi-terms/#section-3
    title: Optional[str] = Field(None, description="A human-readable title given to the resource.")
    description: Optional[str] = Field(
        None, description="A short description of the resource.",
    )
    isActive: Optional[bool] = Field(default=True, description="Whether the resource is still actively maintained.")
    isPrivate: Optional[bool] = Field(
        default=True, description="Whether the resource is private to team members with appropriate authorisation."
    )


class MetadataBaseCreate(MetadataBaseSchema):
    pass


class MetadataBaseUpdate(MetadataBaseSchema):
    identifier: UUID = Field(..., description="Automatically generated unique identity for the resource.")


class MetadataBaseInDBBase(MetadataBaseSchema):
    # Identifier managed programmatically
    identifier: UUID = Field(..., description="Automatically generated unique identity for the resource.")
    created: date = Field(..., description="Automatically generated date resource was created.")
    isActive: bool = Field(..., description="Whether the resource is still actively maintained.")
    isPrivate: bool = Field(
        ..., description="Whether the resource is private to team members with appropriate authorisation."
    )

    class Config:
        # https://github.com/samuelcolvin/pydantic/issues/1334#issuecomment-745434257
        # Call PydanticModel.from_orm(dbQuery)
        orm_mode = True
