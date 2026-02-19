"""
Enrichr — email validation utility
Blocks disposable addresses before they hit your database.

Setup: add ENRICHR_API_KEY to your .env
Get a free key at https://enrichrapi.dev (1,000 calls/month free)
"""

import os
from typing import Any

import httpx

_BASE = os.getenv("ENRICHR_BASE_URL", "https://enrichrapi.dev")


async def validate_email(email: str) -> dict[str, Any] | None:
    """
    Validate an email address via Enrichr.

    Returns None if ENRICHR_API_KEY is not set (graceful degradation).
    Returns None on any network error so signup is never blocked by a failed API call.

    Response fields:
        valid (bool)       — passes format + MX check
        format_ok (bool)   — RFC-5322 format valid
        mx_ok (bool)       — domain has MX records
        disposable (bool)  — known throwaway provider
        normalized (str)   — lowercased, plus-removed canonical form
        domain (str)       — email domain
    """
    key = os.getenv("ENRICHR_API_KEY")
    if not key:
        return None

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.post(
                f"{_BASE}/v1/enrich/email",
                headers={"X-Api-Key": key},
                json={"email": email},
            )
        if not resp.is_success:
            return None
        return resp.json().get("data")
    except Exception:
        return None


async def is_disposable_email(email: str) -> bool:
    """
    Returns True if the email is from a known disposable/throwaway provider.
    Safe to call in API routes — returns False on any network error.

    Usage:
        if await is_disposable_email(user_in.email):
            raise HTTPException(status_code=422, detail="Disposable email addresses are not allowed.")
    """
    result = await validate_email(email)
    return result.get("disposable", False) if result else False
