from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.get("/test/")
def read_item() -> Any:
    return {"message": "Hello World"}
