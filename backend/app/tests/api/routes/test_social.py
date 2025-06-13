"""
Tests for social features endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import User
from app.tests.utils.test_client import TestClientWrapper, assert_successful_response, assert_error_response
from app.tests.utils.test_db import (
    create_test_user, 
    create_test_workout_post, 
    create_test_follow_relationship
)
from app.tests.utils.utils import random_email, random_lower_string


def test_create_workout_post(test_client: TestClientWrapper, db: Session):
    """Test creating a workout post."""
    # Create a user
    email = random_email()
    password = random_lower_string()
    user = create_test_user(db, email=email, password=password)
    
    # Login
    auth_headers = test_client.login(email, password)
    
    # Create workout post
    post_data = {
        "title": "Morning Run",
        "description": "Great 5k run this morning",
        "workout_type": "Running",
        "duration_minutes": 30,
        "calories_burned": 350
    }
    
    response = test_client.post("/social/workout-posts/", headers=auth_headers, json=post_data)
    post = assert_successful_response(response)
    
    assert post["title"] == post_data["title"]
    assert post["description"] == post_data["description"]
    assert post["workout_type"] == post_data["workout_type"]
    assert post["duration_minutes"] == post_data["duration_minutes"]
    assert post["calories_burned"] == post_data["calories_burned"]
    assert post["user_id"] == str(user.id)


def test_get_workout_post(test_client: TestClientWrapper, db: Session):
    """Test getting a workout post by ID."""
    # Create a user
    email = random_email()
    password = random_lower_string()
    user = create_test_user(db, email=email, password=password)
    
    # Create a workout post
    post = create_test_workout_post(
        db, 
        user_id=user.id, 
        title="Evening Yoga", 
        workout_type="Yoga"
    )
    
    # Login
    auth_headers = test_client.login(email, password)
    
    # Get the post
    response = test_client.get(f"/social/workout-posts/{post.id}", headers=auth_headers)
    post_data = assert_successful_response(response)
    
    assert post_data["id"] == str(post.id)
    assert post_data["title"] == post.title
    assert post_data["workout_type"] == post.workout_type


def test_update_workout_post(test_client: TestClientWrapper, db: Session):
    """Test updating a workout post."""
    # Create a user
    email = random_email()
    password = random_lower_string()
    user = create_test_user(db, email=email, password=password)
    
    # Create a workout post
    post = create_test_workout_post(
        db, 
        user_id=user.id, 
        title="Evening Yoga", 
        workout_type="Yoga"
    )
    
    # Login
    auth_headers = test_client.login(email, password)
    
    # Update the post
    update_data = {
        "title": "Updated Yoga Session",
        "duration_minutes": 45
    }
    
    response = test_client.patch(
        f"/social/workout-posts/{post.id}", 
        headers=auth_headers, 
        json=update_data
    )
    updated_post = assert_successful_response(response)
    
    assert updated_post["id"] == str(post.id)
    assert updated_post["title"] == update_data["title"]
    assert updated_post["duration_minutes"] == update_data["duration_minutes"]
    assert updated_post["workout_type"] == post.workout_type  # Unchanged


def test_delete_workout_post(test_client: TestClientWrapper, db: Session):
    """Test deleting a workout post."""
    # Create a user
    email = random_email()
    password = random_lower_string()
    user = create_test_user(db, email=email, password=password)
    
    # Create a workout post
    post = create_test_workout_post(
        db, 
        user_id=user.id, 
        title="Evening Yoga", 
        workout_type="Yoga"
    )
    
    # Login
    auth_headers = test_client.login(email, password)
    
    # Delete the post
    response = test_client.delete(f"/social/workout-posts/{post.id}", headers=auth_headers)
    assert_successful_response(response)
    
    # Verify post is deleted
    response = test_client.get(f"/social/workout-posts/{post.id}", headers=auth_headers)
    assert_error_response(response, status_code=404)


def test_follow_user(test_client: TestClientWrapper, db: Session):
    """Test following another user."""
    # Create two users
    follower_email = random_email()
    follower_password = random_lower_string()
    follower = create_test_user(db, email=follower_email, password=follower_password)
    
    followed_email = random_email()
    followed_password = random_lower_string()
    followed = create_test_user(db, email=followed_email, password=followed_password)
    
    # Login as follower
    auth_headers = test_client.login(follower_email, follower_password)
    
    # Follow the other user
    response = test_client.post(
        f"/social/users/{followed.id}/follow", 
        headers=auth_headers
    )
    follow_data = assert_successful_response(response)
    
    assert follow_data["success"] is True
    
    # Verify follow relationship in DB
    from app.models.social import UserFollow
    from sqlmodel import select
    
    statement = select(UserFollow).where(
        UserFollow.follower_id == follower.id,
        UserFollow.followed_id == followed.id
    )
    follow = db.exec(statement).first()
    assert follow is not None


def test_unfollow_user(test_client: TestClientWrapper, db: Session):
    """Test unfollowing a user."""
    # Create two users
    follower_email = random_email()
    follower_password = random_lower_string()
    follower = create_test_user(db, email=follower_email, password=follower_password)
    
    followed_email = random_email()
    followed_password = random_lower_string()
    followed = create_test_user(db, email=followed_email, password=followed_password)
    
    # Create follow relationship
    create_test_follow_relationship(db, follower_id=follower.id, followed_id=followed.id)
    
    # Login as follower
    auth_headers = test_client.login(follower_email, follower_password)
    
    # Unfollow the user
    response = test_client.delete(
        f"/social/users/{followed.id}/follow", 
        headers=auth_headers
    )
    unfollow_data = assert_successful_response(response)
    
    assert unfollow_data["success"] is True
    
    # Verify follow relationship is removed from DB
    from app.models.social import UserFollow
    from sqlmodel import select
    
    statement = select(UserFollow).where(
        UserFollow.follower_id == follower.id,
        UserFollow.followed_id == followed.id
    )
    follow = db.exec(statement).first()
    assert follow is None


def test_get_user_followers(test_client: TestClientWrapper, db: Session):
    """Test getting a user's followers."""
    # Create users
    user_email = random_email()
    user_password = random_lower_string()
    user = create_test_user(db, email=user_email, password=user_password)
    
    follower1_email = random_email()
    follower1 = create_test_user(db, email=follower1_email, password="password")
    
    follower2_email = random_email()
    follower2 = create_test_user(db, email=follower2_email, password="password")
    
    # Create follow relationships
    create_test_follow_relationship(db, follower_id=follower1.id, followed_id=user.id)
    create_test_follow_relationship(db, follower_id=follower2.id, followed_id=user.id)
    
    # Login
    auth_headers = test_client.login(user_email, user_password)
    
    # Get followers
    response = test_client.get(f"/social/users/{user.id}/followers", headers=auth_headers)
    followers_data = assert_successful_response(response)
    
    assert "data" in followers_data
    assert "count" in followers_data
    assert followers_data["count"] == 2
    
    follower_emails = [follower["email"] for follower in followers_data["data"]]
    assert follower1_email in follower_emails
    assert follower2_email in follower_emails


def test_get_user_following(test_client: TestClientWrapper, db: Session):
    """Test getting users that a user is following."""
    # Create users
    user_email = random_email()
    user_password = random_lower_string()
    user = create_test_user(db, email=user_email, password=user_password)
    
    followed1_email = random_email()
    followed1 = create_test_user(db, email=followed1_email, password="password")
    
    followed2_email = random_email()
    followed2 = create_test_user(db, email=followed2_email, password="password")
    
    # Create follow relationships
    create_test_follow_relationship(db, follower_id=user.id, followed_id=followed1.id)
    create_test_follow_relationship(db, follower_id=user.id, followed_id=followed2.id)
    
    # Login
    auth_headers = test_client.login(user_email, user_password)
    
    # Get following
    response = test_client.get(f"/social/users/{user.id}/following", headers=auth_headers)
    following_data = assert_successful_response(response)
    
    assert "data" in following_data
    assert "count" in following_data
    assert following_data["count"] == 2
    
    following_emails = [followed["email"] for followed in following_data["data"]]
    assert followed1_email in following_emails
    assert followed2_email in following_emails


def test_get_feed(test_client: TestClientWrapper, db: Session):
    """Test getting a user's feed of workout posts."""
    # Create users
    user_email = random_email()
    user_password = random_lower_string()
    user = create_test_user(db, email=user_email, password=user_password)
    
    followed_email = random_email()
    followed = create_test_user(db, email=followed_email, password="password")
    
    # Create follow relationship
    create_test_follow_relationship(db, follower_id=user.id, followed_id=followed.id)
    
    # Create workout posts for followed user
    post1 = create_test_workout_post(
        db, 
        user_id=followed.id, 
        title="Morning Run", 
        workout_type="Running"
    )
    
    post2 = create_test_workout_post(
        db, 
        user_id=followed.id, 
        title="Evening Yoga", 
        workout_type="Yoga"
    )
    
    # Login
    auth_headers = test_client.login(user_email, user_password)
    
    # Get feed
    response = test_client.get("/social/feed", headers=auth_headers)
    feed_data = assert_successful_response(response)
    
    assert "data" in feed_data
    assert "count" in feed_data
    assert feed_data["count"] == 2
    
    post_titles = [post["title"] for post in feed_data["data"]]
    assert "Morning Run" in post_titles
    assert "Evening Yoga" in post_titles