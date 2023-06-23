from datetime import timedelta
from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.get("/_health")
async def health(
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    return "OK"
