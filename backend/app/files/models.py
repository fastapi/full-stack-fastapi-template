from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from app.ocrs.constants import OcrJobStatus
from app.utils import get_datetime_utc


class File(SQLModel, table=True):
    __tablename__ = "files"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=255)
    size: int
    url: str | None = None
    bank: str | None = Field(default=None, max_length=255)
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # ty:ignore[invalid-argument-type]
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id", nullable=False, ondelete="CASCADE"
    )

class FileJob(SQLModel, table=True):
    __tablename__ = "file_jobs"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    job_id: str = Field(max_length=255, index=True)
    file_id: uuid.UUID = Field(foreign_key="files.id", nullable=False, ondelete="CASCADE")
    state: str = Field(default=OcrJobStatus.PENDING, max_length=50)
    model: str | None = Field(default=None, max_length=100)
    total_pages: int | None = None
    extracted_pages: int | None = None
    start_time: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))  # ty:ignore[invalid-argument-type]
    end_time: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))  # ty:ignore[invalid-argument-type]
    json_url: str | None = Field(default=None, max_length=4000)
    markdown_url: str | None = Field(default=None, max_length=4000)
    err_msg: str | None = Field(default=None, max_length=500)
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # ty:ignore[invalid-argument-type]
    )
