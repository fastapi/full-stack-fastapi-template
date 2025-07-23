# ruff: noqa: ARG001

from typing import Any

from fastapi import APIRouter

from app.api.deps import SessionDep

router = APIRouter(tags=["private"], prefix="/private")


@router.get("/private/", response_model=dict)
def private_dashboard(session: SessionDep) -> Any:
    """
    Private dashboard.
    """

    return {"message": "Private dashboard"}
