"""Movie search and details routes (OMDB integration)"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Movie,
    MoviePublic,
    MovieRatingStats,
    MovieSearchPublic,
    Rating,
)
from app.services.omdb import OMDBError, get_omdb_service

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/search", response_model=MovieSearchPublic)
async def search_movies(
    session: SessionDep,
    current_user: CurrentUser,
    q: str = Query(..., min_length=1, description="Search query"),
    year: str | None = Query(None, description="Filter by year"),
    type: str | None = Query(None, description="Filter by type: movie, series, episode"),
    page: int = Query(1, ge=1, description="Page number"),
) -> Any:
    """
    Search movies via OMDB API.
    Results are not cached (search results change frequently).
    """
    try:
        omdb = get_omdb_service()
        results, total = await omdb.search_movies(
            query=q,
            year=year,
            type=type,
            page=page,
        )
        return MovieSearchPublic(data=results, total_results=total)
    except OMDBError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/{imdb_id}", response_model=MoviePublic)
async def get_movie(
    session: SessionDep,
    current_user: CurrentUser,
    imdb_id: str,
    refresh: bool = Query(False, description="Force refresh from OMDB"),
) -> Any:
    """
    Get movie details by IMDB ID.
    Fetches from OMDB and caches if not already cached or stale.
    """
    try:
        omdb = get_omdb_service()
        movie = await omdb.get_or_fetch_movie(
            session=session,
            imdb_id=imdb_id,
            force_refresh=refresh,
        )
        return movie
    except OMDBError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{imdb_id}/ratings", response_model=MovieRatingStats)
def get_movie_ratings(
    session: SessionDep,
    current_user: CurrentUser,
    imdb_id: str,
) -> Any:
    """
    Get aggregated rating stats for a movie.
    """
    # First ensure movie exists in cache
    statement = select(Movie).where(Movie.imdb_id == imdb_id)
    movie = session.exec(statement).first()

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # Get rating stats
    stats_statement = select(
        func.avg(Rating.score).label("average_rating"),
        func.count(Rating.id).label("rating_count"),
    ).where(Rating.movie_id == movie.id)

    result = session.exec(stats_statement).one()

    return MovieRatingStats(
        movie_id=movie.id,
        average_rating=float(result.average_rating or 0),
        rating_count=result.rating_count or 0,
    )
