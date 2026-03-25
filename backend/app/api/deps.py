import hashlib
import logging
import ssl
import time
from typing import Optional

import certifi
import httpx
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from nanoid import generate

from app.core.db import get_db
from app.config import settings
from kila_models.models import UsersTable
from kila_models.models.database import UserSubscriptionTable
from app.utils.subscription import create_free_trial_subscription

logger = logging.getLogger(__name__)

# HTTP Bearer scheme for JWT authentication
security = HTTPBearer()

# SSL context using certifi certificates (fixes macOS SSL issues)
ssl_context = ssl.create_default_context(cafile=certifi.where())

# Clerk JWKS client — caches public keys automatically
CLERK_JWKS_URL = settings.clerk_jwks_url
jwks_client = PyJWKClient(CLERK_JWKS_URL, cache_keys=True, ssl_context=ssl_context)

# Clerk Backend API base URL
CLERK_API_URL = "https://api.clerk.com/v1"

# ── Token-to-user cache ──────────────────────────────────────────────
# Maps token_hash -> (user_id, expires_at_epoch)
# Avoids calling Clerk JWKS + DB lookup on every request.
# Entries expire after TOKEN_CACHE_HOURS hours.
TOKEN_CACHE_HOURS = 10
_token_cache: dict[str, tuple[str, float]] = {}


def _token_hash(token: str) -> str:
    """SHA-256 hash of the bearer token (never store raw tokens)."""
    return hashlib.sha256(token.encode()).hexdigest()


def _cache_get(token: str) -> Optional[str]:
    """Return cached user_id if token is cached and not expired, else None."""
    h = _token_hash(token)
    entry = _token_cache.get(h)
    if entry is None:
        return None
    user_id, expires_at = entry
    if time.time() > expires_at:
        del _token_cache[h]
        return None
    return user_id


def _cache_set(token: str, user_id: str) -> None:
    """Store token -> user_id mapping with expiration."""
    h = _token_hash(token)
    expires_at = time.time() + TOKEN_CACHE_HOURS * 3600
    _token_cache[h] = (user_id, expires_at)


# ── Clerk token verification ─────────────────────────────────────────

def verify_clerk_token(token: str) -> Optional[dict]:
    """
    Verify a Clerk-issued JWT using RS256 and Clerk's JWKS endpoint.
    Returns the decoded payload or None if verification fails.
    """
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Clerk token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid Clerk token: {e}")
        return None
    except Exception as e:
        logger.error(f"Clerk token verification error: {e}")
        return None


# ── FastAPI dependency ────────────────────────────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UsersTable:
    """
    FastAPI dependency that extracts and validates a Clerk JWT from the Authorization header.
    Uses an in-memory cache (10h TTL) to avoid re-verifying the same token on every request.
    On cache miss: verifies with Clerk JWKS, looks up / auto-creates user in DB, then caches.
    """
    token = credentials.credentials

    # ── Fast path: check cache first ──
    cached_user_id = _cache_get(token)
    if cached_user_id:
        stmt = select(UsersTable).where(UsersTable.user_id == cached_user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user and user.is_active:
            return user
        # User gone or deactivated – fall through to full verification

    # ── Slow path: verify token with Clerk ──
    payload = verify_clerk_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    clerk_user_id = payload.get("sub")
    if not clerk_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: missing sub",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Look up user by external_user_id (Clerk ID)
    stmt = select(UsersTable).where(UsersTable.external_user_id == clerk_user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        # Auto-create user on first login via Clerk
        # Fetch real user data (email, name) from Clerk Backend API
        email = None
        user_name = None

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{CLERK_API_URL}/users/{clerk_user_id}",
                    headers={"Authorization": f"Bearer {settings.clerk_secret_key}"},
                )
                if resp.status_code == 200:
                    clerk_user = resp.json()
                    # Get primary email from email_addresses array
                    primary_email_id = clerk_user.get("primary_email_address_id")
                    for addr in clerk_user.get("email_addresses", []):
                        if addr.get("id") == primary_email_id:
                            email = addr.get("email_address")
                            break
                    # Fallback: use first email if primary not matched
                    if not email and clerk_user.get("email_addresses"):
                        email = clerk_user["email_addresses"][0].get("email_address")

                    # Get name
                    first = clerk_user.get("first_name") or ""
                    last = clerk_user.get("last_name") or ""
                    user_name = f"{first} {last}".strip() or None

                    logger.info(f"Fetched Clerk user data: email={email}, name={user_name}")
                else:
                    logger.warning(f"Failed to fetch Clerk user {clerk_user_id}: {resp.status_code}")
        except Exception as e:
            logger.error(f"Error fetching Clerk user data: {e}")

        if not email:
            logger.warning(f"No email found for Clerk user {clerk_user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not retrieve user email from Clerk",
            )

        # Check if a user with this email already exists (pre-Clerk user)
        existing_stmt = select(UsersTable).where(UsersTable.email == email)
        existing_result = await db.execute(existing_stmt)
        existing_user = existing_result.scalar_one_or_none()

        if existing_user:
            # Link existing user to Clerk by setting external_user_id
            existing_user.external_user_id = clerk_user_id
            if user_name and not existing_user.user_name:
                existing_user.user_name = user_name
            # Ensure subscription exists (idempotent — for users created before this feature)
            sub_stmt = select(UserSubscriptionTable).where(UserSubscriptionTable.user_id == existing_user.user_id)
            sub_result = await db.execute(sub_stmt)
            if not sub_result.scalar_one_or_none():
                await create_free_trial_subscription(existing_user.user_id, db)
            await db.commit()
            await db.refresh(existing_user)
            logger.info(f"Linked existing user {existing_user.user_id} to Clerk: {email} (clerk_id={clerk_user_id})")
            user = existing_user
        else:
            # Create new user
            new_user = UsersTable(
                user_id=generate(size=10),
                external_user_id=clerk_user_id,
                email=email,
                user_name=user_name,
                password_hash=None,
                is_active=True,
                is_verified=True,
            )

            db.add(new_user)
            await db.flush()
            await db.refresh(new_user)
            await create_free_trial_subscription(new_user.user_id, db)
            await db.commit()
            await db.refresh(new_user)

            logger.info(f"Auto-created user from Clerk: {email} (clerk_id={clerk_user_id})")
            user = new_user

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    # ── Cache the token -> user_id mapping ──
    _cache_set(token, user.user_id)

    return user


async def require_super_user(
    current_user: UsersTable = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UsersTable:
    """FastAPI dependency: raise 403 if the current user is not a super user."""
    result = await db.execute(
        select(UserSubscriptionTable.is_super_user).where(
            UserSubscriptionTable.user_id == current_user.user_id
        )
    )
    row = result.one_or_none()
    if not row or not row.is_super_user:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
