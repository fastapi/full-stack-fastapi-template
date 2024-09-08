from typing import Any

from fastapi import APIRouter
from sqlmodel import  select
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page

from app.models import LookupJobTitles, LookupJobType
from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
)

router = APIRouter()

@router.get("/job-title")
async def read_job_titles(session:SessionDep) -> Page[LookupJobTitles]:
    """
    Read all job titles
    """
    return paginate(session, select(LookupJobTitles))


@router.get("/job-type")
async def read_job_type(session:SessionDep) -> Page[LookupJobType]:
    """
    Read all job type
    """
    return paginate(session, select(LookupJobType))