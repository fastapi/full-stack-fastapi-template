"""Personal watchlist routes"""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import col, func, select
from sqlmodel.sql.expression import SelectOfScalar

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Movie,
    UserWatchlist,
    UserWatchlistCreate,
    UserWatchlistPublic,
    UserWatchlistsPublic,
    UserWatchlistUpdate,
    UserWatchlistWithMovie,
    WatchlistStatus,
    get_datetime_utc,
)
from app.services.omdb import OMDBError, get_omdb_service

router = APIRouter(prefix="/users/me/watchlist", tags=["watchlist"])


@router.get("/", response_model=UserWatchlistsPublic)
def get_my_watchlist(
    session: SessionDep,
    current_user: CurrentUser,
    status: WatchlistStatus | None = Query(None, description="Filter by status"),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get current user's watchlist with movie details.
    """
    # Base query
    base_conditions = [UserWatchlist.user_id == current_user.id]
    if status:
        base_conditions.append(UserWatchlist.status == status)

    # Count query
    count_statement: SelectOfScalar[int] = (
        select(func.count())
        .select_from(UserWatchlist)
        .where(*base_conditions)
    )
    count = session.exec(count_statement).one()

    # Fetch entries with movies
    statement = (
        select(UserWatchlist)
        .where(*base_conditions)
        .order_by(col(UserWatchlist.added_at).desc())
        .offset(skip)
        .limit(limit)
    )
    entries = session.exec(statement).all()

    # Manually load movies for each entry
    results: list[UserWatchlistWithMovie] = []
    for entry in entries:
        movie = session.get(Movie, entry.movie_id)
        if movie:
            results.append(
                UserWatchlistWithMovie(
                    id=entry.id,
                    status=entry.status,
                    notes=entry.notes,
                    movie_id=entry.movie_id,
                    watched_at=entry.watched_at,
                    added_at=entry.added_at,
                    movie=movie,  # type: ignore
                )
            )

    return UserWatchlistsPublic(data=results, count=count)


@router.post("/", response_model=UserWatchlistPublic)
async def add_to_watchlist(
    session: SessionDep,
    current_user: CurrentUser,
    watchlist_in: UserWatchlistCreate,
) -> Any:
    """
    Add a movie to personal watchlist.
    Movie will be fetched and cached from OMDB if not already cached.
    """
    # Get or fetch movie
    try:
        omdb = get_omdb_service()
        movie = await omdb.get_or_fetch_movie(
            session=session,
            imdb_id=watchlist_in.movie_imdb_id,
        )
    except OMDBError as e:
        raise HTTPException(status_code=404, detail=f"Movie not found: {e}")

    # Check if already in watchlist
    existing = session.exec(
        select(UserWatchlist).where(
            UserWatchlist.user_id == current_user.id,
            UserWatchlist.movie_id == movie.id,
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Movie already in watchlist",
        )

    # Create watchlist entry
    entry = UserWatchlist(
        user_id=current_user.id,
        movie_id=movie.id,
        status=watchlist_in.status,
        notes=watchlist_in.notes,
        watched_at=get_datetime_utc()
        if watchlist_in.status == WatchlistStatus.WATCHED
        else None,
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)

    return entry


@router.patch("/{watchlist_id}", response_model=UserWatchlistPublic)
def update_watchlist_entry(
    session: SessionDep,
    current_user: CurrentUser,
    watchlist_id: uuid.UUID,
    watchlist_in: UserWatchlistUpdate,
) -> Any:
    """
    Update a watchlist entry (status, notes, watched_at).
    """
    entry = session.get(UserWatchlist, watchlist_id)

    if not entry:
        raise HTTPException(status_code=404, detail="Watchlist entry not found")

    if entry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_dict = watchlist_in.model_dump(exclude_unset=True)

    # Auto-set watched_at when status changes to watched
    if (
        watchlist_in.status == WatchlistStatus.WATCHED
        and entry.status != WatchlistStatus.WATCHED
        and "watched_at" not in update_dict
    ):
        update_dict["watched_at"] = get_datetime_utc()

    entry.sqlmodel_update(update_dict)
    session.add(entry)
    session.commit()
    session.refresh(entry)

    return entry


@router.delete("/{watchlist_id}")
def remove_from_watchlist(
    session: SessionDep,
    current_user: CurrentUser,
    watchlist_id: uuid.UUID,
) -> Message:
    """
    Remove a movie from personal watchlist.
    """
    entry = session.get(UserWatchlist, watchlist_id)

    if not entry:
        raise HTTPException(status_code=404, detail="Watchlist entry not found")

    if entry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(entry)
    session.commit()

    return Message(message="Removed from watchlist successfully")
