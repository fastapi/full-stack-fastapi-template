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


def is_mutual_follow(*, session: Session, user1_id: uuid.UUID, user2_id: uuid.UUID) -> bool:
    """
    Check if two users follow each other (mutual follow).
    """
    # Check if user1 follows user2 AND user2 follows user1
    user1_follows_user2 = is_following(session=session, follower_id=user1_id, followed_id=user2_id)
    user2_follows_user1 = is_following(session=session, follower_id=user2_id, followed_id=user1_id)
    
    return user1_follows_user2 and user2_follows_user1


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
    *, session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100, feed_type: str = "personal"
) -> Tuple[List[WorkoutPost], int]:
    """
    Get workout posts based on feed type with privacy filtering.
    
    Args:
        session: Database session
        user_id: Current user's ID
        skip: Number of posts to skip for pagination
        limit: Maximum number of posts to return
        feed_type: "personal", "public", or "combined"
    """
    if feed_type == "public":
        return get_public_feed_posts(session=session, user_id=user_id, skip=skip, limit=limit)
    elif feed_type == "combined":
        return get_combined_feed_posts(session=session, user_id=user_id, skip=skip, limit=limit)
    else:  # personal feed
        return get_personal_feed_posts(session=session, user_id=user_id, skip=skip, limit=limit)


def get_personal_feed_posts(
    *, session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Tuple[List[WorkoutPost], int]:
    """
    Get workout posts from users that the specified user follows (personal feed).
    Includes privacy filtering: private posts only visible if mutual follow.
    """
    # Get IDs of users that the current user follows
    following_statement = (
        select(UserFollow.followed_id)
        .where(UserFollow.follower_id == user_id)
    )
    following_ids = session.exec(following_statement).all()
    
    # Include the user's own posts in the feed
    following_ids.append(user_id)
    
    # Build privacy filter conditions
    privacy_conditions = []
    
    for followed_id in following_ids:
        if followed_id == user_id:
            # User's own posts - always visible
            privacy_conditions.append(
                and_(
                    WorkoutPost.user_id == user_id
                )
            )
        else:
            # Posts from followed users
            is_mutual = is_mutual_follow(session=session, user1_id=user_id, user2_id=followed_id)
            
            if is_mutual:
                # Mutual follow - can see both public and private posts
                privacy_conditions.append(
                    WorkoutPost.user_id == followed_id
                )
            else:
                # Not mutual - only public posts
                privacy_conditions.append(
                    and_(
                        WorkoutPost.user_id == followed_id,
                        WorkoutPost.is_public == True
                    )
                )
    
    if not privacy_conditions:
        return [], 0
    
    # Combine all conditions with OR
    combined_condition = or_(*privacy_conditions)
    
    # Count posts
    count_statement = (
        select(func.count())
        .select_from(WorkoutPost)
        .where(combined_condition)
    )
    count = session.exec(count_statement).one()
    
    # Get posts with pagination
    statement = (
        select(WorkoutPost)
        .where(combined_condition)
        .order_by(WorkoutPost.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    posts = session.exec(statement).all()
    
    return posts, count


def get_public_feed_posts(
    *, session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Tuple[List[WorkoutPost], int]:
    """
    Get all public workout posts from all users (discovery feed).
    """
    # Count all public posts
    count_statement = (
        select(func.count())
        .select_from(WorkoutPost)
        .where(WorkoutPost.is_public == True)
    )
    count = session.exec(count_statement).one()
    
    # Get public posts with pagination
    statement = (
        select(WorkoutPost)
        .where(WorkoutPost.is_public == True)
        .order_by(WorkoutPost.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    posts = session.exec(statement).all()
    
    return posts, count


def get_combined_feed_posts(
    *, session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Tuple[List[WorkoutPost], int]:
    """
    Get combined feed: personal feed + additional public posts.
    """
    # Get personal feed posts first
    personal_posts, personal_count = get_personal_feed_posts(
        session=session, user_id=user_id, skip=0, limit=limit * 2  # Get more to mix
    )
    
    # Get personal post IDs to exclude from public feed
    personal_post_ids = [post.id for post in personal_posts]
    
    # Get additional public posts not in personal feed
    public_condition = and_(
        WorkoutPost.is_public == True,
        ~WorkoutPost.id.in_(personal_post_ids) if personal_post_ids else True
    )
    
    additional_public_statement = (
        select(WorkoutPost)
        .where(public_condition)
        .order_by(WorkoutPost.created_at.desc())
        .limit(limit)
    )
    additional_public_posts = session.exec(additional_public_statement).all()
    
    # Combine and sort by created_at
    all_posts = personal_posts + additional_public_posts
    all_posts.sort(key=lambda x: x.created_at, reverse=True)
    
    # Apply pagination to combined results
    paginated_posts = all_posts[skip:skip + limit]
    
    # Count would be total of personal + additional public (approximation)
    total_count = personal_count + len(additional_public_posts)
    
    return paginated_posts, total_count


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


def search_users(
    *,
    session: Session,
    query: str,
    current_user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 20
) -> Tuple[List[dict], int]:
    """
    Search for users by full_name or email (case-insensitive, partial matches).
    Returns users with their social stats and is_following status.
    Excludes the current user from results.
    """
    # Create the search pattern for case-insensitive partial matching
    search_pattern = f"%{query.lower()}%"
    
    # Base query to find users matching the search criteria
    base_query = (
        select(User)
        .where(
            and_(
                User.id != current_user_id,  # Exclude current user
                or_(
                    func.lower(User.full_name).like(search_pattern),
                    func.lower(User.email).like(search_pattern)
                )
            )
        )
    )
    
    # Count total matching users
    count_statement = select(func.count()).select_from(base_query.subquery())
    count = session.exec(count_statement).one()
    
    # Get paginated results
    users_statement = base_query.offset(skip).limit(limit)
    users = session.exec(users_statement).all()
    
    # Build result with social stats and is_following status
    result = []
    for user in users:
        # Get follower and following counts
        follower_count = get_follower_count(session=session, user_id=user.id)
        following_count = get_following_count(session=session, user_id=user.id)
        
        # Check if current user is following this user
        is_following_user = is_following(
            session=session,
            follower_id=current_user_id,
            followed_id=user.id
        )
        
        # Create user dict with extended info
        user_dict = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "gender": user.gender,
            "date_of_birth": user.date_of_birth,
            "weight": user.weight,
            "height": user.height,
            "follower_count": follower_count,
            "following_count": following_count,
            "is_following": is_following_user
        }
        result.append(user_dict)
    
    return result, count