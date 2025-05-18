"""
User service.

This module provides business logic for user operations.
"""
import uuid
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from pydantic import EmailStr

from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import get_password_hash, verify_password
from app.modules.users.domain.models import User
from app.modules.users.domain.events import UserCreatedEvent
from app.modules.users.domain.models import (
    UserCreate,
    UserPublic,
    UserRegister,
    UserUpdate,
    UserUpdateMe,
    UsersPublic
)
from app.modules.users.repository.user_repo import UserRepository
from app.shared.exceptions import NotFoundException, ValidationException

# Configure logger
logger = get_logger("user_service")


class UserService:
    """
    Service for user operations.

    This class provides business logic for user operations.
    """

    def __init__(self, user_repo: UserRepository):
        """
        Initialize service with user repository.

        Args:
            user_repo: User repository
        """
        self.user_repo = user_repo

    def get_user(self, user_id: str | uuid.UUID) -> User:
        """
        Get a user by ID.

        Args:
            user_id: User ID

        Returns:
            User

        Raises:
            NotFoundException: If user not found
        """
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise NotFoundException(message=f"User with ID {user_id} not found")

        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.

        Args:
            email: User email

        Returns:
            User if found, None otherwise
        """
        return self.user_repo.get_by_email(email)

    def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> Tuple[List[User], int]:
        """
        Get multiple users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: Only include active users if True

        Returns:
            Tuple of (list of users, total count)
        """
        users = self.user_repo.get_multi(
            skip=skip, limit=limit, active_only=active_only
        )
        count = self.user_repo.count(active_only=active_only)

        return users, count

    def create_user(self, user_create: UserCreate) -> User:
        """
        Create a new user.

        Args:
            user_create: User creation data

        Returns:
            Created user

        Raises:
            ValidationException: If email already exists
        """
        # Check if user with this email already exists
        if self.user_repo.exists_by_email(user_create.email):
            raise ValidationException(message="Email already registered")

        # Hash password
        hashed_password = get_password_hash(user_create.password)

        user = User(
            email=user_create.email,
            hashed_password=hashed_password,
            full_name=user_create.full_name,
            is_superuser=user_create.is_superuser,
            is_active=user_create.is_active,
        )

        # Save user to database
        created_user = self.user_repo.create(user)

        # Publish user created event
        event = UserCreatedEvent(
            user_id=created_user.id,
            email=created_user.email,
            full_name=created_user.full_name,
        )
        event.publish()

        logger.info(f"Published user.created event for user {created_user.id}")

        return created_user

    def register_user(self, user_register: UserRegister) -> User:
        """
        Register a new user (normal user, not superuser).

        Args:
            user_register: User registration data

        Returns:
            Registered user

        Raises:
            ValidationException: If email already exists
        """
        # Convert to UserCreate
        user_create = UserCreate(
            email=user_register.email,
            password=user_register.password,
            full_name=user_register.full_name,
            is_superuser=False,
            is_active=True,
        )

        return self.create_user(user_create)

    def update_user(self, user_id: str | uuid.UUID, user_update: UserUpdate) -> User:
        """
        Update a user.

        Args:
            user_id: User ID
            user_update: User update data

        Returns:
            Updated user

        Raises:
            NotFoundException: If user not found
            ValidationException: If email already exists
        """
        # Get existing user
        user = self.get_user(user_id)

        # Check email uniqueness if it's being updated
        if user_update.email and user_update.email != user.email:
            if self.user_repo.exists_by_email(user_update.email):
                raise ValidationException(message="Email already registered")
            user.email = user_update.email

        # Update other fields
        if user_update.full_name is not None:
            user.full_name = user_update.full_name

        if user_update.is_active is not None:
            user.is_active = user_update.is_active

        if user_update.is_superuser is not None:
            user.is_superuser = user_update.is_superuser

        # Update password if provided
        if user_update.password:
            user.hashed_password = get_password_hash(user_update.password)

        return self.user_repo.update(user)

    def update_user_me(
        self, current_user: User, user_update: UserUpdateMe
    ) -> User:
        """
        Update a user's own profile.

        Args:
            current_user: Current user
            user_update: User update data

        Returns:
            Updated user

        Raises:
            ValidationException: If email already exists
        """
        # Get a fresh user object from the database to avoid session issues
        # The current_user object might be attached to a different session
        user = self.get_user(current_user.id)

        # Check email uniqueness if it's being updated
        if user_update.email and user_update.email != user.email:
            if self.user_repo.exists_by_email(user_update.email):
                raise ValidationException(message="Email already registered")
            user.email = user_update.email

        # Update other fields
        if user_update.full_name is not None:
            user.full_name = user_update.full_name

        return self.user_repo.update(user)

    def update_password(
        self, current_user: User, current_password: str, new_password: str
    ) -> User:
        """
        Update a user's password.

        Args:
            current_user: Current user
            current_password: Current password
            new_password: New password

        Returns:
            Updated user

        Raises:
            ValidationException: If current password is incorrect
        """
        # Verify current password
        if not verify_password(current_password, current_user.hashed_password):
            raise ValidationException(message="Incorrect password")

        # Get a fresh user object from the database to avoid session issues
        user = self.get_user(current_user.id)

        # Update password
        user.hashed_password = get_password_hash(new_password)

        return self.user_repo.update(user)

    def delete_user(self, user_id: str | uuid.UUID) -> None:
        """
        Delete a user.

        Args:
            user_id: User ID

        Raises:
            NotFoundException: If user not found
        """
        # Get existing user
        user = self.get_user(user_id)

        # Delete user
        self.user_repo.delete(user)

    def create_initial_superuser(self) -> Optional[User]:
        """
        Create initial superuser from settings if it doesn't exist.

        Returns:
            Created superuser or None if already exists
        """
        # Check if superuser already exists
        if self.user_repo.exists_by_email(settings.FIRST_SUPERUSER):
            return None

        # Create superuser
        superuser = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name="Initial Superuser",
            is_superuser=True,
            is_active=True,
        )

        return self.create_user(superuser)

    # Public model conversions

    def to_public(self, user: User) -> UserPublic:
        """
        Convert user to public model.

        Args:
            user: User to convert

        Returns:
            Public user
        """
        return UserPublic.model_validate(user)

    def to_public_list(self, users: List[User], count: int) -> UsersPublic:
        """
        Convert list of users to public model.

        Args:
            users: Users to convert
            count: Total count

        Returns:
            Public users list
        """
        return UsersPublic(
            data=[self.to_public(user) for user in users],
            count=count,
        )