import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Post,
    PostCreate,
    PostPublic,
    PostUpdate,
    PostsPublic,
    Message,
)

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=PostsPublic)
def read_posts(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve all posts.
    """
    count_statement = select(func.count()).select_from(Post)
    count = session.exec(count_statement).one()

    statement = select(Post).offset(skip).limit(limit)
    posts = session.exec(statement).all()

    return PostsPublic(data=posts, count=count)


@router.post("/", response_model=PostPublic)
def create_post(
    *,
    session: SessionDep,
    post_in: PostCreate,
    current_user: CurrentUser
) -> Any:
    """
    Create a new post.
    """
    new_post = Post(
        user_id=current_user.id,
        content=post_in.content,
        image1_url=post_in.image1_url,
        image2_url=post_in.image2_url,
        image3_url=post_in.image3_url,
    )
    session.add(new_post)
    session.commit()
    session.refresh(new_post)
    return new_post


@router.get("/{post_id}", response_model=PostPublic)
def read_post_by_id(post_id: uuid.UUID, session: SessionDep) -> Any:
    """
    Get a specific post by ID.
    """
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.patch("/{post_id}", response_model=PostPublic)
def update_post(
    *,
    session: SessionDep,
    post_id: uuid.UUID,
    post_in: PostUpdate,
    current_user: CurrentUser
) -> Any:
    """
    Update a post.
    """
    db_post = session.get(Post, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")

    post_data = post_in.model_dump(exclude_unset=True)
    db_post.sqlmodel_update(post_data)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


@router.delete("/{post_id}", response_model=Message)
def delete_post(
    session: SessionDep, post_id: uuid.UUID, current_user: CurrentUser
) -> Any:
    """
    Delete a post.
    """
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")

    session.delete(post)
    session.commit()
    return Message(message="Post deleted successfully")
