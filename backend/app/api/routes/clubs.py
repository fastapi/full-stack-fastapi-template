"""Club routes for movie clubs feature"""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import col, func, or_, select
from sqlmodel.sql.expression import SelectOfScalar

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Club,
    ClubCreate,
    ClubMember,
    ClubMemberPublic,
    ClubMemberWithUser,
    ClubMembersPublic,
    ClubPublic,
    ClubsPublic,
    ClubUpdate,
    ClubVisibility,
    ClubWatchlist,
    ClubWatchlistCreate,
    ClubWatchlistPublic,
    ClubWatchlistsPublic,
    ClubWatchlistVote,
    ClubWatchlistVotePublic,
    ClubWatchlistWithMovie,
    ClubWithMembers,
    MemberRole,
    Message,
    Movie,
    User,
    VoteType,
    get_datetime_utc,
)
from app.services.omdb import OMDBError, get_omdb_service

router = APIRouter(prefix="/clubs", tags=["clubs"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_user_membership(
    session: SessionDep, club_id: uuid.UUID, user_id: uuid.UUID
) -> ClubMember | None:
    """Get user's membership in a club"""
    return session.exec(
        select(ClubMember).where(
            ClubMember.club_id == club_id, ClubMember.user_id == user_id
        )
    ).first()


def require_membership(
    session: SessionDep, club_id: uuid.UUID, user_id: uuid.UUID
) -> ClubMember:
    """Require user to be a member of the club"""
    membership = get_user_membership(session, club_id, user_id)
    if not membership or membership.role == MemberRole.PENDING:
        raise HTTPException(status_code=403, detail="You are not a member of this club")
    return membership


def require_admin(
    session: SessionDep, club_id: uuid.UUID, user_id: uuid.UUID
) -> ClubMember:
    """Require user to be admin or owner of the club"""
    membership = get_user_membership(session, club_id, user_id)
    if not membership or membership.role not in [MemberRole.OWNER, MemberRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return membership


def require_owner(
    session: SessionDep, club_id: uuid.UUID, user_id: uuid.UUID
) -> ClubMember:
    """Require user to be owner of the club"""
    membership = get_user_membership(session, club_id, user_id)
    if not membership or membership.role != MemberRole.OWNER:
        raise HTTPException(status_code=403, detail="Owner privileges required")
    return membership


# ============================================================================
# CLUB CRUD
# ============================================================================


@router.get("/", response_model=ClubsPublic)
def list_clubs(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List all public clubs and clubs the user is a member of.
    """
    # Get IDs of clubs user is a member of
    user_club_ids = session.exec(
        select(ClubMember.club_id).where(ClubMember.user_id == current_user.id)
    ).all()

    # Count
    count_statement: SelectOfScalar[int] = (
        select(func.count())
        .select_from(Club)
        .where(
            or_(
                Club.visibility == ClubVisibility.PUBLIC,
                Club.id.in_(user_club_ids),  # type: ignore
            )
        )
    )
    count = session.exec(count_statement).one()

    # Fetch clubs
    statement = (
        select(Club)
        .where(
            or_(
                Club.visibility == ClubVisibility.PUBLIC,
                Club.id.in_(user_club_ids),  # type: ignore
            )
        )
        .order_by(col(Club.created_at).desc())
        .offset(skip)
        .limit(limit)
    )
    clubs = session.exec(statement).all()

    return ClubsPublic(data=[ClubPublic.model_validate(c) for c in clubs], count=count)


@router.post("/", response_model=ClubPublic)
def create_club(
    session: SessionDep,
    current_user: CurrentUser,
    club_in: ClubCreate,
) -> Any:
    """
    Create a new club. The creator becomes the owner.
    """
    club = Club.model_validate(club_in)
    session.add(club)
    session.commit()
    session.refresh(club)

    # Add creator as owner
    membership = ClubMember(
        club_id=club.id,
        user_id=current_user.id,
        role=MemberRole.OWNER,
    )
    session.add(membership)
    session.commit()

    return club


@router.get("/{club_id}", response_model=ClubWithMembers)
def get_club(
    session: SessionDep,
    current_user: CurrentUser,
    club_id: uuid.UUID,
) -> Any:
    """
    Get club details with member list.
    """
    club = session.get(Club, club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    # Check access
    membership = get_user_membership(session, club_id, current_user.id)
    if club.visibility != ClubVisibility.PUBLIC and not membership:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get members with user details
    members_query = select(ClubMember).where(ClubMember.club_id == club_id)
    members = session.exec(members_query).all()

    members_with_users = []
    for member in members:
        user = session.get(User, member.user_id)
        if user:
            members_with_users.append(
                ClubMemberWithUser(
                    id=member.id,
                    club_id=member.club_id,
                    user_id=member.user_id,
                    role=member.role,
                    joined_at=member.joined_at,
                    user=user,  # type: ignore
                )
            )

    return ClubWithMembers(
        id=club.id,
        name=club.name,
        description=club.description,
        cover_image_url=club.cover_image_url,
        visibility=club.visibility,
        rules=club.rules,
        theme_color=club.theme_color,
        created_at=club.created_at,
        updated_at=club.updated_at,
        members=members_with_users,
        member_count=len(members_with_users),
    )


@router.patch("/{club_id}", response_model=ClubPublic)
def update_club(
    session: SessionDep,
    current_user: CurrentUser,
    club_id: uuid.UUID,
    club_in: ClubUpdate,
) -> Any:
    """
    Update club details. Requires admin or owner.
    """
    club = session.get(Club, club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    require_admin(session, club_id, current_user.id)

    update_dict = club_in.model_dump(exclude_unset=True)
    update_dict["updated_at"] = get_datetime_utc()
    club.sqlmodel_update(update_dict)
    session.add(club)
    session.commit()
    session.refresh(club)

    return club


@router.delete("/{club_id}")
def delete_club(
    session: SessionDep,
    current_user: CurrentUser,
    club_id: uuid.UUID,
) -> Message:
    """
    Delete a club. Requires owner.
    """
    club = session.get(Club, club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    require_owner(session, club_id, current_user.id)

    session.delete(club)
    session.commit()

    return Message(message="Club deleted successfully")


# ============================================================================
# MEMBERSHIP
# ============================================================================


@router.post("/{club_id}/join", response_model=ClubMemberPublic)
def join_club(
    session: SessionDep,
    current_user: CurrentUser,
    club_id: uuid.UUID,
) -> Any:
    """
    Join a club. For invite-only clubs, creates pending membership.
    """
    club = session.get(Club, club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    # Check if already a member
    existing = get_user_membership(session, club_id, current_user.id)
    if existing:
        raise HTTPException(status_code=400, detail="Already a member of this club")

    # Determine initial role based on visibility
    if club.visibility == ClubVisibility.INVITE_ONLY:
        role = MemberRole.PENDING
    else:
        role = MemberRole.MEMBER

    if club.visibility == ClubVisibility.PRIVATE:
        raise HTTPException(status_code=403, detail="This club is private")

    membership = ClubMember(
        club_id=club_id,
        user_id=current_user.id,
        role=role,
    )
    session.add(membership)
    session.commit()
    session.refresh(membership)

    return membership


@router.delete("/{club_id}/leave")
def leave_club(
    session: SessionDep,
    current_user: CurrentUser,
    club_id: uuid.UUID,
) -> Message:
    """
    Leave a club.
    """
    membership = get_user_membership(session, club_id, current_user.id)
    if not membership:
        raise HTTPException(status_code=404, detail="Not a member of this club")

    if membership.role == MemberRole.OWNER:
        # Check if there are other admins to transfer ownership
        other_admins = session.exec(
            select(ClubMember).where(
                ClubMember.club_id == club_id,
                ClubMember.user_id != current_user.id,
                ClubMember.role.in_([MemberRole.ADMIN, MemberRole.OWNER]),  # type: ignore
            )
        ).first()
        if not other_admins:
            raise HTTPException(
                status_code=400,
                detail="Cannot leave: you are the only owner. Transfer ownership first or delete the club.",
            )

    session.delete(membership)
    session.commit()

    return Message(message="Left the club successfully")


@router.patch("/{club_id}/members/{user_id}", response_model=ClubMemberPublic)
def update_member_role(
    session: SessionDep,
    current_user: CurrentUser,
    club_id: uuid.UUID,
    user_id: uuid.UUID,
    role: MemberRole = Query(...),
) -> Any:
    """
    Update a member's role. Requires admin (for member changes) or owner (for admin changes).
    """
    # Get target membership
    membership = get_user_membership(session, club_id, user_id)
    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")

    # Get current user's membership
    current_membership = get_user_membership(session, club_id, current_user.id)
    if not current_membership:
        raise HTTPException(status_code=403, detail="Not a member of this club")

    # Permission checks
    if role == MemberRole.OWNER:
        require_owner(session, club_id, current_user.id)
        # Transfer ownership: demote current owner to admin
        current_membership.role = MemberRole.ADMIN
        session.add(current_membership)
    elif role == MemberRole.ADMIN or membership.role == MemberRole.ADMIN:
        require_owner(session, club_id, current_user.id)
    else:
        require_admin(session, club_id, current_user.id)

    membership.role = role
    session.add(membership)
    session.commit()
    session.refresh(membership)

    return membership


@router.delete("/{club_id}/members/{user_id}")
def remove_member(
    session: SessionDep,
    current_user: CurrentUser,
    club_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Message:
    """
    Remove a member from the club. Requires admin or owner.
    """
    membership = get_user_membership(session, club_id, user_id)
    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")

    # Cannot remove owner
    if membership.role == MemberRole.OWNER:
        raise HTTPException(status_code=400, detail="Cannot remove the owner")

    # Only owner can remove admins
    if membership.role == MemberRole.ADMIN:
        require_owner(session, club_id, current_user.id)
    else:
        require_admin(session, club_id, current_user.id)

    session.delete(membership)
    session.commit()

    return Message(message="Member removed successfully")


# ============================================================================
# CLUB WATCHLIST
# ============================================================================


@router.get("/{club_id}/watchlist", response_model=ClubWatchlistsPublic)
def get_club_watchlist(
    session: SessionDep,
    current_user: CurrentUser,
    club_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get club's watchlist with movies and vote counts.
    """
    club = session.get(Club, club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    require_membership(session, club_id, current_user.id)

    # Count
    count_statement: SelectOfScalar[int] = (
        select(func.count())
        .select_from(ClubWatchlist)
        .where(ClubWatchlist.club_id == club_id)
    )
    count = session.exec(count_statement).one()

    # Fetch entries
    statement = (
        select(ClubWatchlist)
        .where(ClubWatchlist.club_id == club_id)
        .order_by(col(ClubWatchlist.added_at).desc())
        .offset(skip)
        .limit(limit)
    )
    entries = session.exec(statement).all()

    results: list[ClubWatchlistWithMovie] = []
    for entry in entries:
        movie = session.get(Movie, entry.movie_id)
        if movie:
            # Get vote counts
            upvotes = session.exec(
                select(func.count())
                .select_from(ClubWatchlistVote)
                .where(
                    ClubWatchlistVote.watchlist_entry_id == entry.id,
                    ClubWatchlistVote.vote_type == VoteType.UPVOTE,
                )
            ).one()
            downvotes = session.exec(
                select(func.count())
                .select_from(ClubWatchlistVote)
                .where(
                    ClubWatchlistVote.watchlist_entry_id == entry.id,
                    ClubWatchlistVote.vote_type == VoteType.DOWNVOTE,
                )
            ).one()

            # Get user's vote
            user_vote_obj = session.exec(
                select(ClubWatchlistVote).where(
                    ClubWatchlistVote.watchlist_entry_id == entry.id,
                    ClubWatchlistVote.user_id == current_user.id,
                )
            ).first()
            user_vote = user_vote_obj.vote_type if user_vote_obj else None

            results.append(
                ClubWatchlistWithMovie(
                    id=entry.id,
                    club_id=entry.club_id,
                    movie_id=entry.movie_id,
                    added_by_user_id=entry.added_by_user_id,
                    notes=entry.notes,
                    added_at=entry.added_at,
                    movie=movie,  # type: ignore
                    upvotes=upvotes,
                    downvotes=downvotes,
                    user_vote=user_vote,
                )
            )

    return ClubWatchlistsPublic(data=results, count=count)


@router.post("/{club_id}/watchlist", response_model=ClubWatchlistPublic)
async def add_to_club_watchlist(
    session: SessionDep,
    current_user: CurrentUser,
    club_id: uuid.UUID,
    watchlist_in: ClubWatchlistCreate,
) -> Any:
    """
    Add a movie to the club's watchlist.
    """
    club = session.get(Club, club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    require_membership(session, club_id, current_user.id)

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
        select(ClubWatchlist).where(
            ClubWatchlist.club_id == club_id,
            ClubWatchlist.movie_id == movie.id,
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Movie already in club watchlist",
        )

    entry = ClubWatchlist(
        club_id=club_id,
        movie_id=movie.id,
        added_by_user_id=current_user.id,
        notes=watchlist_in.notes,
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)

    return entry


@router.delete("/{club_id}/watchlist/{entry_id}")
def remove_from_club_watchlist(
    session: SessionDep,
    current_user: CurrentUser,
    club_id: uuid.UUID,
    entry_id: uuid.UUID,
) -> Message:
    """
    Remove a movie from the club's watchlist.
    Requires admin/owner or being the user who added it.
    """
    entry = session.get(ClubWatchlist, entry_id)
    if not entry or entry.club_id != club_id:
        raise HTTPException(status_code=404, detail="Watchlist entry not found")

    membership = require_membership(session, club_id, current_user.id)

    # Allow removal if user added it or is admin/owner
    if entry.added_by_user_id != current_user.id:
        if membership.role not in [MemberRole.OWNER, MemberRole.ADMIN]:
            raise HTTPException(status_code=403, detail="Cannot remove this entry")

    session.delete(entry)
    session.commit()

    return Message(message="Removed from club watchlist")


# ============================================================================
# VOTING
# ============================================================================


@router.post("/{club_id}/watchlist/{entry_id}/vote", response_model=ClubWatchlistVotePublic)
def vote_on_watchlist_entry(
    session: SessionDep,
    current_user: CurrentUser,
    club_id: uuid.UUID,
    entry_id: uuid.UUID,
    vote_type: VoteType = Query(...),
) -> Any:
    """
    Vote on a watchlist entry. Toggle if voting same type again.
    """
    entry = session.get(ClubWatchlist, entry_id)
    if not entry or entry.club_id != club_id:
        raise HTTPException(status_code=404, detail="Watchlist entry not found")

    require_membership(session, club_id, current_user.id)

    # Check for existing vote
    existing_vote = session.exec(
        select(ClubWatchlistVote).where(
            ClubWatchlistVote.watchlist_entry_id == entry_id,
            ClubWatchlistVote.user_id == current_user.id,
        )
    ).first()

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            # Toggle off - remove vote
            session.delete(existing_vote)
            session.commit()
            return Message(message="Vote removed")  # type: ignore
        else:
            # Change vote type
            existing_vote.vote_type = vote_type
            existing_vote.created_at = get_datetime_utc()
            session.add(existing_vote)
            session.commit()
            session.refresh(existing_vote)
            return existing_vote

    # Create new vote
    vote = ClubWatchlistVote(
        watchlist_entry_id=entry_id,
        user_id=current_user.id,
        vote_type=vote_type,
    )
    session.add(vote)
    session.commit()
    session.refresh(vote)

    return vote
