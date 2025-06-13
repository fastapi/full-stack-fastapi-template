import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from sqlmodel import Session, select, func, or_, and_

from app.models.social import UserFollow, WorkoutPost, WorkoutPostCreate, WorkoutPostUpdate
from app.models.user import User


# User Follow Operations

def follow_user(*, session: Session, follower_id: uuid.UUID, followed_id: uuid.UUID) -> UserFollow:
    """
    Create a follow relationship between users.
    """
    # Check if the follow relationship already exists
    statement = select(UserFollow).where(
        and_(
            UserFollow.follower_id == follower_id,
            UserFollow.followed_id == followed_id
        )
    )
    existing_follow = session.exec(statement).first()
    
    if existing_follow:
        return existing_follow
    
    # Create new follow relationship
    follow = UserFollow(follower_id=follower_id, followed_id=followed_id)
    session.add(follow)
    session.commit()
    session.refresh(follow)
    return follow


def unfollow_user(*, session: Session, follower_id: uuid.UUID, followed_id: uuid.UUID) -> bool:
    """
    Remove a follow relationship between users.
    """
    statement = select(UserFollow).where(
        and_(
            UserFollow.follower_id == follower_id,
            UserFollow.followed_id == followed_id
        )
    )
    follow = session.exec(statement).first()
    
    if follow:
        session.delete(follow)
        session.commit()
        return True
    return False


def get_followers(*, session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Tuple[List[User], int]:
    """
    Get users who follow the specified user.
    """
    # Count followers
    count_statement = (
        select(func.count())
        .select_from(UserFollow)
        .where(UserFollow.followed_id == user_id)
    )
    count = session.exec(count_statement).one()
    
    # Get followers with pagination
    statement = (
        select(User)
        .join(UserFollow, User.id == UserFollow.follower_id)
        .where(UserFollow.followed_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    followers = session.exec(statement).all()
    
    return followers, count


def get_following(*, session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Tuple[List[User], int]:
    """
    Get users that the specified user follows.
    """
    # Count following
    count_statement = (
        select(func.count())
        .select_from(UserFollow)
        .where(UserFollow.follower_id == user_id)
    )
    count = session.exec(count_statement).one()
    
    # Get following with pagination
    statement = (
        select(User)
        .join(UserFollow, User.id == UserFollow.followed_id)
        .where(UserFollow.follower_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    following = session.exec(statement).all()
    
    return following, count


def is_following(*, session: Session, follower_id: uuid.UUID, followed_id: uuid.UUID) -> bool:
    """
    Check if a user is following another user.
    """
    statement = select(UserFollow).where(
        and_(
            UserFollow.follower_id == follower_id,
            UserFollow.followed_id == followed_id
        )
    )
    follow = session.exec(statement).first()
    return follow is not None


def get_follower_count(*, session: Session, user_id: uuid.UUID) -> int:
    """
    Get the number of followers for a user.
    """
    statement = (
        select(func.count())
        .select_from(UserFollow)
        .where(UserFollow.followed_id == user_id)
    )
    return session.exec(statement).one()


def get_following_count(*, session: Session, user_id: uuid.UUID) -> int:
    """
    Get the number of users a user is following.
    """
    statement = (
        select(func.count())
        .select_from(UserFollow)
        .where(UserFollow.follower_id == user_id)
    )
    return session.exec(statement).one()


# Workout Post Operations

def create_workout_post(*, session: Session, post_in: WorkoutPostCreate, user_id: uuid.UUID) -> WorkoutPost:
    """
    Create a new workout post.
    """
    db_post = WorkoutPost.model_validate(post_in, update={"user_id": user_id})
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


def get_workout_post(*, session: Session, post_id: uuid.UUID) -> Optional[WorkoutPost]:
    """
    Get a workout post by ID.
    """
    return session.get(WorkoutPost, post_id)


def get_user_workout_posts(
    *, session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Tuple[List[WorkoutPost], int]:
    """
    Get workout posts for a specific user.
    """
    count_statement = (
        select(func.count())
        .select_from(WorkoutPost)
        .where(WorkoutPost.user_id == user_id)
    )
    count = session.exec(count_statement).one()
    
    statement = (
        select(WorkoutPost)
        .where(WorkoutPost.user_id == user_id)
        .order_by(WorkoutPost.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    posts = session.exec(statement).all()
    
    return posts, count


def get_feed_posts(
    *, session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Tuple[List[WorkoutPost], int]:
    """
    Get workout posts from users that the specified user follows.
    """
    # Get IDs of users that the current user follows
    following_statement = (
        select(UserFollow.followed_id)
        .where(UserFollow.follower_id == user_id)
    )
    following_ids = session.exec(following_statement).all()
    
    # Include the user's own posts in the feed
    following_ids.append(user_id)
    
    # Count posts from followed users
    count_statement = (
        select(func.count())
        .select_from(WorkoutPost)
        .where(WorkoutPost.user_id.in_(following_ids))
    )
    count = session.exec(count_statement).one()
    
    # Get posts from followed users with pagination
    statement = (
        select(WorkoutPost)
        .where(WorkoutPost.user_id.in_(following_ids))
        .order_by(WorkoutPost.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    posts = session.exec(statement).all()
    
    return posts, count


def update_workout_post(
    *, session: Session, db_post: WorkoutPost, post_in: WorkoutPostUpdate
) -> WorkoutPost:
    """
    Update a workout post.
    """
    update_dict = post_in.model_dump(exclude_unset=True)
    update_dict["updated_at"] = datetime.utcnow()
    db_post.sqlmodel_update(update_dict)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


def delete_workout_post(*, session: Session, post_id: uuid.UUID) -> bool:
    """
    Delete a workout post.
    """
    post = session.get(WorkoutPost, post_id)
    if post:
        session.delete(post)
        session.commit()
        return True
    return False