import enum
import uuid
from datetime import datetime, timezone

from pydantic import EmailStr
from sqlalchemy import Column, DateTime, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlmodel import Field, Relationship, SQLModel


class WatchlistStatus(str, enum.Enum):
    WANT_TO_WATCH = "want_to_watch"
    WATCHED = "watched"


class ClubVisibility(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    INVITE_ONLY = "invite_only"


class MemberRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    PENDING = "pending"


class VoteType(str, enum.Enum):
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    watchlist_entries: list["UserWatchlist"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    ratings: list["Rating"] = Relationship(back_populates="user", cascade_delete=True)
    club_memberships: list["ClubMember"] = Relationship(
        back_populates="user", cascade_delete=True
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# ============================================================================
# MOVIE MODELS (OMDB Cache)
# ============================================================================


class MovieBase(SQLModel):
    imdb_id: str = Field(max_length=20)
    title: str = Field(max_length=500)
    year: str | None = Field(default=None, max_length=10)
    rated: str | None = Field(default=None, max_length=20)
    released: str | None = Field(default=None, max_length=50)
    runtime: str | None = Field(default=None, max_length=20)
    genre: str | None = Field(default=None, max_length=255)
    director: str | None = Field(default=None, max_length=500)
    writer: str | None = Field(default=None, max_length=1000)
    actors: str | None = Field(default=None, max_length=1000)
    plot: str | None = Field(default=None, sa_column=Column(Text))
    language: str | None = Field(default=None, max_length=255)
    country: str | None = Field(default=None, max_length=255)
    awards: str | None = Field(default=None, max_length=500)
    poster_url: str | None = Field(default=None, max_length=1000)
    imdb_rating: str | None = Field(default=None, max_length=10)
    imdb_votes: str | None = Field(default=None, max_length=20)
    box_office: str | None = Field(default=None, max_length=50)


class Movie(MovieBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    imdb_id: str = Field(unique=True, index=True, max_length=20)
    fetched_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    raw_data: dict = Field(default={}, sa_column=Column(JSON))

    # Relationships
    watchlist_entries: list["UserWatchlist"] = Relationship(
        back_populates="movie", cascade_delete=True
    )
    ratings: list["Rating"] = Relationship(back_populates="movie", cascade_delete=True)
    club_watchlist_entries: list["ClubWatchlist"] = Relationship(
        back_populates="movie", cascade_delete=True
    )


class MoviePublic(MovieBase):
    id: uuid.UUID
    fetched_at: datetime


class MoviesPublic(SQLModel):
    data: list[MoviePublic]
    count: int


class MovieSearchResult(SQLModel):
    """Lightweight movie result from OMDB search"""

    imdb_id: str
    title: str
    year: str | None = None
    poster_url: str | None = None
    type: str | None = None


class MovieSearchPublic(SQLModel):
    data: list[MovieSearchResult]
    total_results: int


class MovieRatingStats(SQLModel):
    """Aggregated rating statistics for a movie"""

    movie_id: uuid.UUID
    average_rating: float
    rating_count: int


# ============================================================================
# USER WATCHLIST MODELS
# ============================================================================


class UserWatchlistBase(SQLModel):
    status: WatchlistStatus = WatchlistStatus.WANT_TO_WATCH
    notes: str | None = Field(default=None, max_length=1000)


class UserWatchlistCreate(SQLModel):
    movie_imdb_id: str = Field(max_length=20)
    status: WatchlistStatus = WatchlistStatus.WANT_TO_WATCH
    notes: str | None = Field(default=None, max_length=1000)


class UserWatchlistUpdate(SQLModel):
    status: WatchlistStatus | None = None
    notes: str | None = Field(default=None, max_length=1000)
    watched_at: datetime | None = None


class UserWatchlist(UserWatchlistBase, table=True):
    __tablename__ = "user_watchlist"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    movie_id: uuid.UUID = Field(
        foreign_key="movie.id", nullable=False, ondelete="CASCADE"
    )
    watched_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    added_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    # Relationships
    user: User | None = Relationship(back_populates="watchlist_entries")
    movie: Movie | None = Relationship(back_populates="watchlist_entries")


class UserWatchlistPublic(UserWatchlistBase):
    id: uuid.UUID
    movie_id: uuid.UUID
    watched_at: datetime | None = None
    added_at: datetime


class UserWatchlistWithMovie(UserWatchlistPublic):
    """Watchlist entry with full movie details"""

    movie: MoviePublic


class UserWatchlistsPublic(SQLModel):
    data: list[UserWatchlistWithMovie]
    count: int


# ============================================================================
# RATING MODELS
# ============================================================================


class RatingBase(SQLModel):
    score: float = Field(ge=1.0, le=5.0)


class RatingCreate(SQLModel):
    movie_imdb_id: str = Field(max_length=20)
    score: float = Field(ge=1.0, le=5.0)
    club_id: uuid.UUID | None = None  # For future club context


class RatingUpdate(SQLModel):
    score: float | None = Field(default=None, ge=1.0, le=5.0)


class Rating(RatingBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    movie_id: uuid.UUID = Field(
        foreign_key="movie.id", nullable=False, ondelete="CASCADE"
    )
    club_id: uuid.UUID | None = Field(
        default=None, foreign_key="club.id", ondelete="SET NULL"
    )
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    # Relationships
    user: User | None = Relationship(back_populates="ratings")
    movie: Movie | None = Relationship(back_populates="ratings")


class RatingPublic(RatingBase):
    id: uuid.UUID
    movie_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class RatingWithMovie(RatingPublic):
    """Rating with full movie details"""

    movie: MoviePublic


class RatingsPublic(SQLModel):
    data: list[RatingWithMovie]
    count: int


# ============================================================================
# CLUB MODELS
# ============================================================================


class ClubBase(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    cover_image_url: str | None = Field(default=None, max_length=1000)
    visibility: ClubVisibility = ClubVisibility.PUBLIC
    rules: str | None = Field(default=None, max_length=2000)
    theme_color: str | None = Field(default=None, max_length=20)


class ClubCreate(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    visibility: ClubVisibility = ClubVisibility.PUBLIC
    rules: str | None = Field(default=None, max_length=2000)
    theme_color: str | None = Field(default=None, max_length=20)


class ClubUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    cover_image_url: str | None = Field(default=None, max_length=1000)
    visibility: ClubVisibility | None = None
    rules: str | None = Field(default=None, max_length=2000)
    theme_color: str | None = Field(default=None, max_length=20)


class Club(ClubBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    # Relationships
    members: list["ClubMember"] = Relationship(
        back_populates="club", cascade_delete=True
    )
    watchlist_entries: list["ClubWatchlist"] = Relationship(
        back_populates="club", cascade_delete=True
    )
    ratings: list["Rating"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Rating.club_id]"}
    )


class ClubPublic(ClubBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ClubsPublic(SQLModel):
    data: list[ClubPublic]
    count: int


# ============================================================================
# CLUB MEMBER MODELS
# ============================================================================


class ClubMemberBase(SQLModel):
    role: MemberRole = MemberRole.MEMBER


class ClubMember(ClubMemberBase, table=True):
    __tablename__ = "club_member"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    club_id: uuid.UUID = Field(
        foreign_key="club.id", nullable=False, ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    joined_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    # Relationships
    club: Club | None = Relationship(back_populates="members")
    user: User | None = Relationship(back_populates="club_memberships")


class ClubMemberPublic(ClubMemberBase):
    id: uuid.UUID
    club_id: uuid.UUID
    user_id: uuid.UUID
    joined_at: datetime


class ClubMemberWithUser(ClubMemberPublic):
    """Club member with user details"""
    user: UserPublic


class ClubMembersPublic(SQLModel):
    data: list[ClubMemberWithUser]
    count: int


class ClubWithMembers(ClubPublic):
    """Club with member list"""
    members: list[ClubMemberWithUser]
    member_count: int


# ============================================================================
# CLUB WATCHLIST MODELS
# ============================================================================


class ClubWatchlistBase(SQLModel):
    notes: str | None = Field(default=None, max_length=1000)


class ClubWatchlistCreate(SQLModel):
    movie_imdb_id: str = Field(max_length=20)
    notes: str | None = Field(default=None, max_length=1000)


class ClubWatchlist(ClubWatchlistBase, table=True):
    __tablename__ = "club_watchlist"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    club_id: uuid.UUID = Field(
        foreign_key="club.id", nullable=False, ondelete="CASCADE"
    )
    movie_id: uuid.UUID = Field(
        foreign_key="movie.id", nullable=False, ondelete="CASCADE"
    )
    added_by_user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    added_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    # Relationships
    club: Club | None = Relationship(back_populates="watchlist_entries")
    movie: Movie | None = Relationship(back_populates="club_watchlist_entries")
    votes: list["ClubWatchlistVote"] = Relationship(
        back_populates="watchlist_entry", cascade_delete=True
    )


class ClubWatchlistPublic(ClubWatchlistBase):
    id: uuid.UUID
    club_id: uuid.UUID
    movie_id: uuid.UUID
    added_by_user_id: uuid.UUID
    added_at: datetime


class ClubWatchlistWithMovie(ClubWatchlistPublic):
    """Club watchlist entry with movie details and vote counts"""
    movie: MoviePublic
    upvotes: int = 0
    downvotes: int = 0
    user_vote: VoteType | None = None


class ClubWatchlistsPublic(SQLModel):
    data: list[ClubWatchlistWithMovie]
    count: int


# ============================================================================
# CLUB WATCHLIST VOTE MODELS
# ============================================================================


class ClubWatchlistVoteBase(SQLModel):
    vote_type: VoteType


class ClubWatchlistVote(ClubWatchlistVoteBase, table=True):
    __tablename__ = "club_watchlist_vote"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    watchlist_entry_id: uuid.UUID = Field(
        foreign_key="club_watchlist.id", nullable=False, ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    # Relationships
    watchlist_entry: ClubWatchlist | None = Relationship(back_populates="votes")


class ClubWatchlistVotePublic(ClubWatchlistVoteBase):
    id: uuid.UUID
    watchlist_entry_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
