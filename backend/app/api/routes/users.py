import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.core.config import settings
from app.core.security import verify_password
from app.models import (
    Message,
    UpdatePassword,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.utils import generate_new_account_email, send_email

# Create a new APIRouter instance for user-related routes
router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def read_users(
    session: SessionDep,  # pyright: ignore [reportInvalidTypeForm] [reportInvalidTypeForm]
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve users.

    This endpoint allows retrieving a list of users with pagination.
    It's protected and can only be accessed by superusers.

    Args:
        session (SessionDep): The database session dependency.
        skip (int): The number of users to skip (for pagination).
        limit (int): The maximum number of users to return.

    Returns:
        UsersPublic: An object containing the list of users and the total count.

    Notes:
        This endpoint is useful for administrative purposes to view all users in the system.
    """
    # Get a list of users with pagination
    users = crud.get_users(session=session, skip=skip, limit=limit)
    # Get the total count of users
    count = crud.get_user_count(session=session)
    # Return the users and count in the UsersPublic model
    return UsersPublic(data=users, count=count)


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
def create_user(
    *,
    session: SessionDep,  # pyright: ignore [reportInvalidTypeForm]
    user_in: UserCreate,
) -> Any:
    """
    Create new user.

    This endpoint allows creating a new user in the system.
    It's protected and can only be accessed by superusers.

    Args:
        session (SessionDep): The database session dependency.
        user_in (UserCreate): The user data to be created.

    Returns:
        UserPublic: The created user's public information.

    Raises:
        HTTPException:
            - 400: If a user with the given email already exists.

    Notes:
        If email sending is enabled, a new account email will be sent to the user.
    """
    # Check if a user with the given email already exists
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    # Create the new user
    user = crud.create_user(session=session, user_create=user_in)
    # If email sending is enabled, send a new account email
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *,
    session: SessionDep,  # pyright: ignore [reportInvalidTypeForm]
    user_in: UserUpdateMe,
    current_user: CurrentUser,
) -> Any:
    """
    Update own user.

    This endpoint allows users to update their own information.
    It's protected and can be accessed by authenticated users.

    Args:
        session (SessionDep): The database session dependency.
        user_in (UserUpdateMe): The user data to be updated.
        current_user (CurrentUser): The current authenticated user.

    Returns:
        UserPublic: The updated user's public information.

    Raises:
        HTTPException:
            - 409: If the new email is already in use by another user.

    Notes:
        Users can update their own information, but not their role or superuser status.
    """
    # If the email is being updated, check if it's already in use
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    # Update the user's attributes
    updated_user = crud.update_user_attributes(
        session=session,
        db_user=current_user,
        user_in=UserUpdate(**user_in.model_dump()),
    )
    return updated_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *,
    session: SessionDep,  # pyright: ignore [reportInvalidTypeForm]
    body: UpdatePassword,
    current_user: CurrentUser,
) -> Any:
    """
    Update own password.

    This endpoint allows users to update their own password.
    It's protected and can be accessed by authenticated users.

    Args:
        session (SessionDep): The database session dependency.
        body (UpdatePassword): The current and new password data.
        current_user (CurrentUser): The current authenticated user.

    Returns:
        Message: A message confirming the password update.

    Raises:
        HTTPException:
            - 400: If the current password is incorrect or if the new password is the same as the current one.

    Notes:
        Users must provide their current password for security reasons.
    """
    # Verify the current password
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    # Ensure the new password is different from the current one
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    # Update the user's password
    crud.update_user_password(
        session=session,
        db_user=current_user,
        new_password=body.new_password,
    )
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.

    This endpoint allows users to retrieve their own information.
    It's protected and can be accessed by authenticated users.

    Args:
        current_user (CurrentUser): The current authenticated user.

    Returns:
        UserPublic: The current user's public information.

    Notes:
        This endpoint is useful for clients to get the latest user information after login.
    """
    # Return the current user's information
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(
    session: SessionDep,  # pyright: ignore [reportInvalidTypeForm]
    current_user: CurrentUser,
) -> Any:
    """
    Delete own user.

    This endpoint allows users to delete their own account.
    It's protected and can be accessed by authenticated users.

    Args:
        session (SessionDep): The database session dependency.
        current_user (CurrentUser): The current authenticated user.

    Returns:
        Message: A message confirming the user deletion.

    Raises:
        HTTPException:
            - 403: If the user is a superuser trying to delete their own account.

    Notes:
        Superusers are not allowed to delete their own accounts for security reasons.
    """
    # Prevent superusers from deleting themselves
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    # Delete the user
    crud.delete_user(session=session, user_id=current_user.id)
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(
    session: SessionDep,  # pyright: ignore [reportInvalidTypeForm]
    user_in: UserRegister,
) -> Any:
    """
    Create new user without the need to be logged in.

    This endpoint allows new users to register in the system.
    It's public and can be accessed without authentication.

    Args:
        session (SessionDep): The database session dependency.
        user_in (UserRegister): The user registration data.

    Returns:
        UserPublic: The created user's public information.

    Raises:
        HTTPException:
            - 400: If a user with the given email already exists.

    Notes:
        This endpoint is typically used for user sign-up functionality.
    """
    # Check if a user with the given email already exists
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    # Create a UserCreate model from the UserRegister input
    user_create = UserCreate.model_validate(user_in)
    # Create the new user
    user = crud.create_user(session=session, user_create=user_create)
    return user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID,
    session: SessionDep,  # pyright: ignore [reportInvalidTypeForm]
    current_user: CurrentUser,
) -> Any:
    """
    Get a specific user by id.

    This endpoint allows retrieving a specific user's information by their ID.
    It's protected and can be accessed by the user themselves or superusers.

    Args:
        user_id (uuid.UUID): The ID of the user to retrieve.
        session (SessionDep): The database session dependency.
        current_user (CurrentUser): The current authenticated user.

    Returns:
        UserPublic: The requested user's public information.

    Raises:
        HTTPException:
            - 403: If the current user doesn't have enough privileges to access the information.
            - 404: If the user with the given ID is not found.

    Notes:
        Regular users can only access their own information, while superusers can access any user's information.
    """
    # Retrieve the user by ID
    user = crud.get_user(session=session, user_id=user_id)
    # Allow users to access their own information
    if user == current_user:
        return user
    # Only superusers can access other users' information
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,  # pyright: ignore [reportInvalidTypeForm]
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.

    This endpoint allows updating a specific user's information.
    It's protected and can only be accessed by superusers.

    Args:
        session (SessionDep): The database session dependency.
        user_id (uuid.UUID): The ID of the user to update.
        user_in (UserUpdate): The user data to be updated.

    Returns:
        UserPublic: The updated user's public information.

    Raises:
        HTTPException:
            - 404: If the user with the given ID is not found.
            - 409: If the new email is already in use by another user.

    Notes:
        This endpoint is typically used for administrative purposes to update any user's information.
    """
    # Retrieve the user by ID
    db_user = crud.get_user(session=session, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    # If the email is being updated, check if it's already in use
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    # Update the user's attributes
    db_user = crud.update_user_attributes(
        session=session, db_user=db_user, user_in=user_in
    )
    return db_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep,  # pyright: ignore [reportInvalidTypeForm]
    current_user: CurrentUser,
    user_id: uuid.UUID,
) -> Message:
    """
    Delete a user.

    This endpoint allows deleting a specific user from the system.
    It's protected and can only be accessed by superusers.

    Args:
        session (SessionDep): The database session dependency.
        current_user (CurrentUser): The current authenticated superuser.
        user_id (uuid.UUID): The ID of the user to delete.

    Returns:
        Message: A message confirming the user deletion.

    Raises:
        HTTPException:
            - 403: If a superuser tries to delete their own account.
            - 404: If the user with the given ID is not found.

    Notes:
        Superusers are not allowed to delete their own accounts for security reasons.
    """
    # Retrieve the user by ID
    user = crud.get_user(session=session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Prevent superusers from deleting themselves
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    # Delete the user
    crud.delete_user(session=session, user_id=user_id)
    return Message(message="User deleted successfully")
