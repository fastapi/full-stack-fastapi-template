"""Movie ratings routes"""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select
from sqlmodel.sql.expression import SelectOfScalar

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Movie,
    Rating,
    RatingCreate,
    RatingPublic,
    RatingsPublic,
    RatingUpdate,
    RatingWithMovie,
    get_datetime_utc,
)
from app.services.omdb import OMDBError, get_omdb_service

router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.post("/", response_model=RatingPublic)
async def create_rating(
    session: SessionDep,
    current_user: CurrentUser,
    rating_in: RatingCreate,
) -> Any:
    """
    Create or update a rating for a movie.
    Only one rating per user per movie is allowed (upsert behavior).
    """
    # Get or fetch movie
    try:
        omdb = get_omdb_service()
        movie = await omdb.get_or_fetch_movie(
            session=session,
            imdb_id=rating_in.movie_imdb_id,
        )
    except OMDBError as e:
        raise HTTPException(status_code=404, detail=f"Movie not found: {e}")

    # Check if rating already exists
    existing = session.exec(
        select(Rating).where(
            Rating.user_id == current_user.id,
            Rating.movie_id == movie.id,
        )
    ).first()

    if existing:
        # Update existing rating
        existing.score = rating_in.score
        existing.updated_at = get_datetime_utc()
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    # Create new rating
    rating = Rating(
        user_id=current_user.id,
        movie_id=movie.id,
        club_id=rating_in.club_id,
        score=rating_in.score,
    )
    session.add(rating)
    session.commit()
    session.refresh(rating)

    return rating


@router.get("/me", response_model=RatingsPublic)
def get_my_ratings(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get current user's ratings with movie details.
    """
    # Count query
    count_statement: SelectOfScalar[int] = (
        select(func.count())
        .select_from(Rating)
        .where(Rating.user_id == current_user.id)
    )
    count = session.exec(count_statement).one()

    # Fetch ratings
    statement = (
        select(Rating)
        .where(Rating.user_id == current_user.id)
        .order_by(col(Rating.updated_at).desc())
        .offset(skip)
        .limit(limit)
    )
    ratings = session.exec(statement).all()

    # Manually load movies for each rating
    results: list[RatingWithMovie] = []
    for rating in ratings:
        movie = session.get(Movie, rating.movie_id)
        if movie:
            results.append(
                RatingWithMovie(
                    id=rating.id,
                    score=rating.score,
                    movie_id=rating.movie_id,
                    created_at=rating.created_at,
                    updated_at=rating.updated_at,
                    movie=movie,  # type: ignore
                )
            )

    return RatingsPublic(data=results, count=count)


@router.patch("/{rating_id}", response_model=RatingPublic)
def update_rating(
    session: SessionDep,
    current_user: CurrentUser,
    rating_id: uuid.UUID,
    rating_in: RatingUpdate,
) -> Any:
    """
    Update a rating score.
    """
    rating = session.get(Rating, rating_id)

    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")

    if rating.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if rating_in.score is not None:
        rating.score = rating_in.score
        rating.updated_at = get_datetime_utc()

    session.add(rating)
    session.commit()
    session.refresh(rating)

    return rating


@router.delete("/{rating_id}")
def delete_rating(
    session: SessionDep,
    current_user: CurrentUser,
    rating_id: uuid.UUID,
) -> Message:
    """
    Delete a rating.
    """
    rating = session.get(Rating, rating_id)

    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")

    if rating.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(rating)
    session.commit()

    return Message(message="Rating deleted successfully")
