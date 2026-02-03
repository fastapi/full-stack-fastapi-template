from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from nanoid import generate
from app.core.db import get_db
from app.core.db import UsersTable
from app.models.user_auth import UserSignupRequest, UserLoginRequest, UserResponse, TokenResponse
from app.utils.auth import hash_password, verify_password, create_access_token, create_refresh_token
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
        user_data: UserSignupRequest,
        db: AsyncSession = Depends(get_db)
):
    """
    Create a new user account

    - **email**: Valid email address (must be unique)
    - **password**: Strong password (min 8 chars, must contain uppercase, lowercase, and digit)
    """
    # Check if user already exists
    stmt = select(UsersTable).where(UsersTable.email == user_data.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    password_hash = hash_password(user_data.password)

    # Create new user
    new_user = UsersTable(
        user_id=generate(size=10),
        email=user_data.email,
        password_hash=password_hash,
        user_name=user_data.full_name,
        is_active=True,
        is_verified=False  # Will be True after email verification
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info(f"New user created: {new_user.email}")

    # Create tokens
    access_token = create_access_token(data={"sub": str(new_user.user_id), "email": new_user.email})
    refresh_token = create_refresh_token(data={"sub": str(new_user.user_id)})

    # Return user data and tokens
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(
        login_data: UserLoginRequest,
        db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password

    Returns access token and refresh token
    """
    # Find user by email
    stmt = select(UsersTable).where(UsersTable.email == login_data.email)
    result = await db.execute(stmt)
    user: UsersTable = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Check if account is locked - this is the future feature
    """
    if user.locked_until and user.locked_until > datetime.now():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account temporarily locked due to too many failed login attempts"
        )
    """

    # Verify password
    if not verify_password(login_data.password, user.password_hash):

        # Increment failed login attempts - this is future feature
        """
        user.failed_login_attempts += 1

        # Lock account after 5 failed attempts
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account locked due to too many failed login attempts. Try again in 15 minutes."
            )

        await db.commit()
        """

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Reset failed login attempts and update last login - reset failed login is a future feature
    """
    user.failed_login_attempts = 0
    user.locked_until = None
    """

    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.user_id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.user_id)})

    logger.info(f"User logged in: {user.email}")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.from_orm(user)
    )
