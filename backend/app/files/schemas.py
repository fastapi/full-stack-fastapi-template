import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Field, SQLModel


class FileBase(SQLModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=255)
    size: int | None = None

class FileCreate(FileBase):
    url: str | None = None

class FilePublic(FileBase):
    id: uuid.UUID
    created_at: datetime | None = None
    user_id: uuid.UUID

class FilesPublic(SQLModel):
    data: list[FilePublic]
    count: int


class FilesStatusRequest(SQLModel):
    file_ids: list[uuid.UUID]


# ---------------------------------------------------------------------------
# FileJob schemas
# ---------------------------------------------------------------------------

class FileJobCreate(SQLModel):
    job_id: str = Field(max_length=255)
    file_id: uuid.UUID
    state: str = Field(max_length=50)
    total_pages: int | None = None
    extracted_pages: int | None = None
    json_url: str | None = Field(default=None, max_length=4000)
    markdown_url: str | None = Field(default=None, max_length=4000)
    err_msg: str | None = Field(default=None, max_length=500)


class FileJobPublic(SQLModel):
    id: uuid.UUID
    job_id: str
    file_id: uuid.UUID
    state: str
    total_pages: int | None = None
    extracted_pages: int | None = None
    json_url: str | None = None
    markdown_url: str | None = None
    err_msg: str | None = None
    created_at: datetime | None = None


class FileWithJobPublic(FilePublic):
    """FilePublic enriched with its associated FileJob (if any)."""
    job: FileJobPublic | None = None


# ---------------------------------------------------------------------------
# Result preview schemas
# ---------------------------------------------------------------------------

class FilePreviewResponse(SQLModel):
    """Parsed OCR result table for a file, ready to render in the front end.

    ``columns`` is the ordered list of column headers and ``rows`` is the table
    content as a list of ``{column: value}`` records — the same data the JSON
    download exports, returned inline for previewing.
    """
    file_id: uuid.UUID
    filename: str
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    markdown_url: str | None = None
