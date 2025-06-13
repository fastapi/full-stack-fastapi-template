import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models.social import (
    UserFollow,
    WorkoutPost,
    WorkoutPostCreate,
    WorkoutPostPublic,
    WorkoutPostsPublic,
    WorkoutPostUpdate,
)
from app.models.token import Message
from app.models.user import User, UserPublic, UserPublicExtended, UsersPublic

router = APIRouter(prefix="/social", tags=["social"])


# User Follow Endpoints

@router.post("/follow/{user_id}", response_model=Message)
def follow_user(
    user_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Follow a user.
    
    This endpoint allows the current user to follow another user.
    
    Parameters:
    - **user_id**: Required. The UUID of the user to follow
    
    Returns a success message confirming the follow action.
    
    Raises:
    - 400: If the user tries to follow themselves
    - 404: If the user to follow doesn't exist
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot follow yourself",
        )
    
    # Check if the user to follow exists
    user_to_follow = crud.get_user_by_id(session=session, user_id=user_id)
    if not user_to_follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Create follow relationship
    crud.follow_user(
        session=session, follower_id=current_user.id, followed_id=user_id
    )
    
    return Message(message=f"You are now following {user_to_follow.full_name or user_to_follow.email}")


@router.delete("/unfollow/{user_id}", response_model=Message)
def unfollow_user(
    user_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Unfollow a user.
    
    This endpoint allows the current user to unfollow a user they are currently following.
    
    Parameters:
    - **user_id**: Required. The UUID of the user to unfollow
    
    Returns a success message confirming the unfollow action.
    
    Raises:
    - 400: If the user tries to unfollow themselves
    - 404: If the user to unfollow doesn't exist
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot unfollow yourself",
        )
    
    # Check if the user to unfollow exists
    user_to_unfollow = crud.get_user_by_id(session=session, user_id=user_id)
    if not user_to_unfollow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Remove follow relationship
    success = crud.unfollow_user(
        session=session, follower_id=current_user.id, followed_id=user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You are not following {user_to_unfollow.full_name or user_to_unfollow.email}",
        )
    
    return Message(message=f"You have unfollowed {user_to_unfollow.full_name or user_to_unfollow.email}")


@router.get("/followers", response_model=UsersPublic)
def get_followers(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Get users who follow the current user.
    """
    followers, count = crud.get_followers(
        session=session, user_id=current_user.id, skip=skip, limit=limit
    )
    
    return UsersPublic(data=followers, count=count)


@router.get("/following", response_model=UsersPublic)
def get_following(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Get users that the current user follows.
    """
    following, count = crud.get_following(
        session=session, user_id=current_user.id, skip=skip, limit=limit
    )
    
    return UsersPublic(data=following, count=count)


@router.get("/user/{user_id}/followers", response_model=UsersPublic)
def get_user_followers(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Get followers of a specific user.
    """
    # Check if the user exists
    user = crud.get_user_by_id(session=session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    followers, count = crud.get_followers(
        session=session, user_id=user_id, skip=skip, limit=limit
    )
    
    return UsersPublic(data=followers, count=count)


@router.get("/user/{user_id}/following", response_model=UsersPublic)
def get_user_following(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Get users that a specific user follows.
    """
    # Check if the user exists
    user = crud.get_user_by_id(session=session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    following, count = crud.get_following(
        session=session, user_id=user_id, skip=skip, limit=limit
    )
    
    return UsersPublic(data=following, count=count)


@router.get("/user/{user_id}/profile", response_model=UserPublicExtended)
def get_user_profile(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a user's profile with follower and following counts.
    """
    # Check if the user exists
    user = crud.get_user_by_id(session=session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Get follower and following counts
    follower_count = crud.get_follower_count(session=session, user_id=user_id)
    following_count = crud.get_following_count(session=session, user_id=user_id)
    
    # Create extended user profile
    user_data = UserPublic.model_validate(user).model_dump()
    user_extended = UserPublicExtended(
        **user_data,
        follower_count=follower_count,
        following_count=following_count
    )
    
    return user_extended


@router.get("/is-following/{user_id}", response_model=dict)
def check_if_following(
    user_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Check if the current user is following a specific user.
    
    This endpoint checks whether the current user is following another user.
    
    Parameters:
    - **user_id**: Required. The UUID of the user to check
    
    Returns a JSON object with a boolean "is_following" field.
    
    Example response:
    ```json
    {
        "is_following": true
    }
    ```
    
    Raises:
    - 404: If the user to check doesn't exist
    """
    # Check if the user exists
    user = crud.get_user_by_id(session=session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    is_following = crud.is_following(
        session=session, follower_id=current_user.id, followed_id=user_id
    )
    
    return {"is_following": is_following}


# Workout Post Endpoints

@router.post("/workout-posts", response_model=WorkoutPostPublic)
def create_workout_post(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    post_in: WorkoutPostCreate
) -> Any:
    """
    Create a new workout post.
    
    This endpoint allows users to create a new workout post to share with followers.
    
    Parameters:
    - **title**: Required. The title of the workout post
    - **description**: Optional. A description of the workout
    - **workout_type**: Required. The type of workout (e.g., Running, Strength, Yoga)
    - **duration_minutes**: Required. The duration of the workout in minutes
    - **calories_burned**: Optional. The number of calories burned during the workout
    
    Returns the created workout post with user information.
    
    Example request body:
    ```json
    {
        "title": "Morning Run",
        "description": "Great 5k run this morning",
        "workout_type": "Running",
        "duration_minutes": 30,
        "calories_burned": 300
    }
    ```
    """
    post = crud.create_workout_post(
        session=session, post_in=post_in, user_id=current_user.id
    )
    
    # Add user's full name to the response
    post_data = WorkoutPostPublic.model_validate(post).model_dump()
    post_data["user_full_name"] = current_user.full_name
    
    return WorkoutPostPublic(**post_data)


@router.get("/workout-posts", response_model=WorkoutPostsPublic)
def get_my_workout_posts(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Get the current user's workout posts.
    
    This endpoint retrieves all workout posts created by the current user.
    
    Parameters:
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return
    
    Returns a list of workout posts and the total count.
    """
    posts, count = crud.get_user_workout_posts(
        session=session, user_id=current_user.id, skip=skip, limit=limit
    )
    
    # Add user's full name to each post
    post_data = []
    for post in posts:
        post_dict = WorkoutPostPublic.model_validate(post).model_dump()
        post_dict["user_full_name"] = current_user.full_name
        post_data.append(WorkoutPostPublic(**post_dict))
    
    return WorkoutPostsPublic(data=post_data, count=count)


@router.get("/user/{user_id}/workout-posts", response_model=WorkoutPostsPublic)
def get_user_workout_posts(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Get a specific user's workout posts.
    """
    # Check if the user exists
    user = crud.get_user_by_id(session=session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    posts, count = crud.get_user_workout_posts(
        session=session, user_id=user_id, skip=skip, limit=limit
    )
    
    # Add user's full name to each post
    post_data = []
    for post in posts:
        post_dict = WorkoutPostPublic.model_validate(post).model_dump()
        post_dict["user_full_name"] = user.full_name
        post_data.append(WorkoutPostPublic(**post_dict))
    
    return WorkoutPostsPublic(data=post_data, count=count)


@router.get("/feed", response_model=WorkoutPostsPublic)
def get_feed(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Get workout posts from users that the current user follows, including their own posts.
    """
    posts, count = crud.get_feed_posts(
        session=session, user_id=current_user.id, skip=skip, limit=limit
    )
    
    # Add user's full name to each post
    post_data = []
    for post in posts:
        post_dict = WorkoutPostPublic.model_validate(post).model_dump()
        # Get the user who created the post
        user = crud.get_user_by_id(session=session, user_id=post.user_id)
        if user:
            post_dict["user_full_name"] = user.full_name
        post_data.append(WorkoutPostPublic(**post_dict))
    
    return WorkoutPostsPublic(data=post_data, count=count)


@router.get("/workout-posts/{post_id}", response_model=WorkoutPostPublic)
def get_workout_post(
    post_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific workout post.
    """
    post = crud.get_workout_post(session=session, post_id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout post not found",
        )
    
    # Add user's full name to the response
    post_data = WorkoutPostPublic.model_validate(post).model_dump()
    user = crud.get_user_by_id(session=session, user_id=post.user_id)
    if user:
        post_data["user_full_name"] = user.full_name
    
    return WorkoutPostPublic(**post_data)


@router.put("/workout-posts/{post_id}", response_model=WorkoutPostPublic)
def update_workout_post(
    *,
    post_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    post_in: WorkoutPostUpdate,
) -> Any:
    """
    Update a workout post.
    """
    post = crud.get_workout_post(session=session, post_id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout post not found",
        )
    
    # Check if the user is the owner of the post
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    post = crud.update_workout_post(
        session=session, db_post=post, post_in=post_in
    )
    
    # Add user's full name to the response
    post_data = WorkoutPostPublic.model_validate(post).model_dump()
    post_data["user_full_name"] = current_user.full_name
    
    return WorkoutPostPublic(**post_data)


@router.delete("/workout-posts/{post_id}", response_model=Message)
def delete_workout_post(
    post_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Delete a workout post.
    """
    post = crud.get_workout_post(session=session, post_id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout post not found",
        )
    
    # Check if the user is the owner of the post or a superuser
    if not current_user.is_superuser and post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    crud.delete_workout_post(session=session, post_id=post_id)
    
    return Message(message="Workout post deleted successfully")