# Vantage - Movie Club Platform Specification

## Overview

**Vantage** is a social movie club platform that enables teams of users to create and manage movie clubs together. Users can discover films via the OMDB database, organize watch parties, rate and discuss movies, and build curated watchlists with their club members.

### Vision

A beautifully designed, retro-inspired application that brings the golden age of cinema club culture into the digital era—combining the communal joy of movie watching with modern collaboration tools.

---

## Design Philosophy

### Visual Identity

**Aesthetic**: Art Deco / Retro Cinema

**Color Palette**:
| Role | Color | Hex |
|------|-------|-----|
| Background (Primary) | Off-White / Cream | `#FAF7F2` |
| Background (Secondary) | Warm Ivory | `#F5F0E6` |
| Primary Accent | Rich Brown | `#8B4513` |
| Secondary Accent | Chocolate | `#5C3317` |
| Dark Accent | Espresso | `#3C2415` |
| Gold Highlight | Antique Gold | `#C9A227` |
| Text (Primary) | Charcoal | `#2C2C2C` |
| Text (Secondary) | Warm Gray | `#6B6B6B` |
| Success | Olive Green | `#6B7B3C` |
| Error | Burgundy | `#8B2942` |

**Typography**:
- **Headers**: Art Deco inspired serif font (e.g., Poiret One, Playfair Display)
- **Body**: Clean readable sans-serif (e.g., Lato, Source Sans Pro)
- **Accents**: Decorative geometric fonts for logos/titles

**Design Elements**:
- Geometric patterns and borders (chevrons, sunbursts, fan motifs)
- Film strip and reel iconography
- Vintage movie poster styling for cards
- Subtle grain/texture overlays
- Gold/bronze metallic accents for premium features
- Rounded art deco frames and containers

---

## Target Users

1. **Movie Enthusiasts** - Individuals passionate about film who want to share their hobby
2. **Friend Groups** - Casual groups looking to organize regular movie nights
3. **Film Students / Critics** - Those seeking structured discussion environments
4. **Corporate Teams** - Office groups building team culture through movie events
5. **Online Communities** - Remote groups coordinating virtual watch parties

---

## Core Features

### 1. User Management (Existing + Extended)

**Existing** (from template):
- User registration and authentication (JWT)
- Profile management
- Password recovery
- Admin/superuser capabilities

**Extended**:
- User avatar upload
- Movie preferences (favorite genres, decades, directors)
- Watch history
- Personal movie ratings
- Public profile pages

### 2. Movie Clubs

**Club Creation & Management**:
- Create clubs with name, description, and cover image
- Set club visibility (public, private, invite-only)
- Define club rules/guidelines
- Club themes (Horror Mondays, 80s Classics, Foreign Films, etc.)

**Membership**:
- Club owner (creator) with full admin rights
- Admins (appointed by owner) - can manage members and content
- Members - can participate in all club activities
- Pending members - awaiting approval for private clubs

**Club Features**:
- Club dashboard with activity feed
- Member directory
- Club statistics (movies watched, total ratings, etc.)
- Club achievements/badges

### 3. Movie Discovery (OMDB Integration)

**Search Capabilities**:
- Search by title, year, type (movie, series, episode)
- Advanced filters (genre, rating, decade)
- Browse popular/trending (cached results)

**Movie Details**:
- Full OMDB data display (plot, cast, director, ratings)
- Movie posters and artwork
- External links (IMDb, Rotten Tomatoes)
- Club-specific ratings aggregation

**Data Caching**:
- Cache OMDB responses to reduce API calls
- Store frequently accessed movies locally
- Background refresh for stale data

### 4. Watchlists

**Personal Watchlists**:
- "Want to Watch" queue
- "Watched" history with dates
- Custom personal lists

**Club Watchlists**:
- Shared club watchlist (members can add/vote)
- "Currently Watching" - active selection
- "Club Favorites" - top-rated by members
- "Watch History" - completed films with dates

**Voting System**:
- Upvote/downvote movies in club watchlist
- Nominate movies for club viewing
- Voting polls for next movie selection

### 5. Ratings & Reviews

**Rating System**:
- 1-5 star rating (half-stars allowed)
- Quick emoji reactions
- Detailed written reviews

**Review Features**:
- Spoiler tagging
- Review likes/helpful votes
- Comment threads on reviews
- Edit/delete own reviews

**Aggregation**:
- Club average rating per movie
- Personal rating history
- Rating trends over time

### 6. Events & Watch Parties

**Event Creation**:
- Schedule movie screenings (date, time, timezone)
- In-person vs. virtual events
- RSVP functionality
- Capacity limits for in-person events

**Watch Party Features**:
- Countdown timer to event
- Streaming service links
- Live chat during screening (for virtual)
- Post-movie discussion threads

**Notifications**:
- Event reminders (24h, 1h before)
- New movie added to watchlist
- Club activity updates
- Review responses

### 7. Discussion Forums

**Discussion Types**:
- Movie-specific discussions
- General club chat
- Theme discussions (Best Villains, Underrated Gems, etc.)
- Off-topic channel

**Features**:
- Threaded replies
- Rich text formatting
- Image/GIF embedding
- Pin important discussions
- Archive old threads

---

## Data Models

### New Models

```
Club
├── id: UUID (PK)
├── name: str (unique per owner)
├── slug: str (URL-friendly, unique)
├── description: str
├── cover_image_url: str | None
├── theme: str | None
├── visibility: enum (public, private, invite_only)
├── owner_id: UUID (FK → User)
├── created_at: datetime
├── updated_at: datetime
└── is_active: bool

ClubMembership
├── id: UUID (PK)
├── club_id: UUID (FK → Club)
├── user_id: UUID (FK → User)
├── role: enum (owner, admin, member)
├── status: enum (active, pending, banned)
├── joined_at: datetime
└── invited_by_id: UUID | None (FK → User)

Movie (cached from OMDB)
├── id: UUID (PK)
├── imdb_id: str (unique, indexed)
├── title: str
├── year: str
├── rated: str | None
├── released: str | None
├── runtime: str | None
├── genre: str | None
├── director: str | None
├── writer: str | None
├── actors: str | None
├── plot: str | None
├── language: str | None
├── country: str | None
├── awards: str | None
├── poster_url: str | None
├── imdb_rating: str | None
├── imdb_votes: str | None
├── box_office: str | None
├── fetched_at: datetime
└── raw_data: JSON (full OMDB response)

ClubWatchlist
├── id: UUID (PK)
├── club_id: UUID (FK → Club)
├── movie_id: UUID (FK → Movie)
├── added_by_id: UUID (FK → User)
├── status: enum (queued, watching, watched, removed)
├── watch_date: datetime | None
├── vote_score: int (default 0)
├── added_at: datetime
└── updated_at: datetime

WatchlistVote
├── id: UUID (PK)
├── watchlist_item_id: UUID (FK → ClubWatchlist)
├── user_id: UUID (FK → User)
├── vote: int (+1 or -1)
└── voted_at: datetime

Rating
├── id: UUID (PK)
├── user_id: UUID (FK → User)
├── movie_id: UUID (FK → Movie)
├── club_id: UUID | None (FK → Club, for club context)
├── score: float (1.0 - 5.0)
├── created_at: datetime
└── updated_at: datetime

Review
├── id: UUID (PK)
├── user_id: UUID (FK → User)
├── movie_id: UUID (FK → Movie)
├── club_id: UUID | None (FK → Club)
├── rating_id: UUID | None (FK → Rating)
├── title: str | None
├── content: str
├── contains_spoilers: bool
├── helpful_count: int
├── created_at: datetime
└── updated_at: datetime

Event
├── id: UUID (PK)
├── club_id: UUID (FK → Club)
├── movie_id: UUID | None (FK → Movie)
├── title: str
├── description: str | None
├── event_type: enum (in_person, virtual, hybrid)
├── location: str | None
├── streaming_link: str | None
├── start_time: datetime (with timezone)
├── end_time: datetime | None
├── capacity: int | None
├── created_by_id: UUID (FK → User)
├── created_at: datetime
└── is_cancelled: bool

EventRSVP
├── id: UUID (PK)
├── event_id: UUID (FK → Event)
├── user_id: UUID (FK → User)
├── status: enum (attending, maybe, declined)
├── responded_at: datetime
└── notes: str | None

Discussion
├── id: UUID (PK)
├── club_id: UUID (FK → Club)
├── movie_id: UUID | None (FK → Movie)
├── author_id: UUID (FK → User)
├── title: str
├── content: str
├── is_pinned: bool
├── is_locked: bool
├── reply_count: int
├── created_at: datetime
└── updated_at: datetime

DiscussionReply
├── id: UUID (PK)
├── discussion_id: UUID (FK → Discussion)
├── author_id: UUID (FK → User)
├── parent_reply_id: UUID | None (FK → self, for threading)
├── content: str
├── created_at: datetime
└── updated_at: datetime

UserWatchlist (personal)
├── id: UUID (PK)
├── user_id: UUID (FK → User)
├── movie_id: UUID (FK → Movie)
├── status: enum (want_to_watch, watched)
├── watched_at: datetime | None
├── added_at: datetime
└── notes: str | None
```

### Relationships Summary

```
User (1) ──────< ClubMembership >────── (N) Club
User (1) ──────< Rating >────────────── (N) Movie
User (1) ──────< Review >────────────── (N) Movie
User (1) ──────< UserWatchlist >─────── (N) Movie
User (1) ──────< EventRSVP >─────────── (N) Event
User (1) ──────< Discussion
User (1) ──────< DiscussionReply

Club (1) ──────< ClubWatchlist >─────── (N) Movie
Club (1) ──────< Event
Club (1) ──────< Discussion

Movie (1) ─────< Rating
Movie (1) ─────< Review
Movie (1) ─────< ClubWatchlist
Movie (1) ─────< Event
Movie (1) ─────< Discussion
```

---

## API Design

### New API Routes

#### Movies (OMDB Integration)

```
GET    /api/v1/movies/search?q={query}&year={year}&type={type}
       → Search OMDB, return paginated results

GET    /api/v1/movies/{imdb_id}
       → Get movie details (fetch from OMDB if not cached)

GET    /api/v1/movies/{imdb_id}/ratings
       → Get all ratings for a movie (filterable by club)

GET    /api/v1/movies/{imdb_id}/reviews
       → Get all reviews for a movie (paginated)
```

#### Clubs

```
POST   /api/v1/clubs/
       → Create new club

GET    /api/v1/clubs/
       → List clubs (public + user's clubs)

GET    /api/v1/clubs/{slug}
       → Get club details

PATCH  /api/v1/clubs/{slug}
       → Update club (owner/admin only)

DELETE /api/v1/clubs/{slug}
       → Delete club (owner only)

GET    /api/v1/clubs/{slug}/members
       → List club members

POST   /api/v1/clubs/{slug}/members
       → Add/invite member (admin+)

PATCH  /api/v1/clubs/{slug}/members/{user_id}
       → Update member role/status

DELETE /api/v1/clubs/{slug}/members/{user_id}
       → Remove member

POST   /api/v1/clubs/{slug}/join
       → Request to join / join public club

POST   /api/v1/clubs/{slug}/leave
       → Leave club
```

#### Club Watchlist

```
GET    /api/v1/clubs/{slug}/watchlist
       → Get club watchlist (filterable by status)

POST   /api/v1/clubs/{slug}/watchlist
       → Add movie to watchlist

PATCH  /api/v1/clubs/{slug}/watchlist/{item_id}
       → Update watchlist item status

DELETE /api/v1/clubs/{slug}/watchlist/{item_id}
       → Remove from watchlist

POST   /api/v1/clubs/{slug}/watchlist/{item_id}/vote
       → Vote on watchlist item (+1/-1)
```

#### Ratings & Reviews

```
POST   /api/v1/ratings/
       → Create rating (movie_id, score, optional club_id)

GET    /api/v1/ratings/me
       → Get current user's ratings

PATCH  /api/v1/ratings/{id}
       → Update rating

DELETE /api/v1/ratings/{id}
       → Delete rating

POST   /api/v1/reviews/
       → Create review

GET    /api/v1/reviews/
       → List reviews (filterable)

PATCH  /api/v1/reviews/{id}
       → Update review

DELETE /api/v1/reviews/{id}
       → Delete review

POST   /api/v1/reviews/{id}/helpful
       → Mark review as helpful
```

#### Events

```
GET    /api/v1/clubs/{slug}/events
       → List club events

POST   /api/v1/clubs/{slug}/events
       → Create event

GET    /api/v1/clubs/{slug}/events/{id}
       → Get event details

PATCH  /api/v1/clubs/{slug}/events/{id}
       → Update event

DELETE /api/v1/clubs/{slug}/events/{id}
       → Cancel/delete event

POST   /api/v1/clubs/{slug}/events/{id}/rsvp
       → RSVP to event

GET    /api/v1/events/upcoming
       → Get user's upcoming events across all clubs
```

#### Discussions

```
GET    /api/v1/clubs/{slug}/discussions
       → List club discussions

POST   /api/v1/clubs/{slug}/discussions
       → Create discussion

GET    /api/v1/clubs/{slug}/discussions/{id}
       → Get discussion with replies

PATCH  /api/v1/clubs/{slug}/discussions/{id}
       → Update discussion

DELETE /api/v1/clubs/{slug}/discussions/{id}
       → Delete discussion

POST   /api/v1/clubs/{slug}/discussions/{id}/replies
       → Add reply

PATCH  /api/v1/discussions/replies/{id}
       → Update reply

DELETE /api/v1/discussions/replies/{id}
       → Delete reply
```

#### Personal Watchlist

```
GET    /api/v1/users/me/watchlist
       → Get personal watchlist

POST   /api/v1/users/me/watchlist
       → Add movie to personal watchlist

PATCH  /api/v1/users/me/watchlist/{id}
       → Update watchlist item

DELETE /api/v1/users/me/watchlist/{id}
       → Remove from watchlist
```

---

## OMDB Integration

### API Details

- **Base URL**: `http://www.omdbapi.com/`
- **API Key**: Required (free tier: 1,000 daily requests)
- **Rate Limiting**: Implement client-side rate limiting

### Integration Strategy

1. **Search Proxy**: Backend proxies OMDB search requests
2. **Caching**: Store movie details in local `Movie` table
3. **Refresh Policy**: Re-fetch if `fetched_at` > 30 days
4. **Fallback**: Show cached data if OMDB is unavailable
5. **Poster Storage**: Consider CDN proxy for poster images

### Environment Variables

```env
OMDB_API_KEY=your_api_key_here
OMDB_CACHE_TTL_DAYS=30
```

---

## Frontend Routes

### New Routes

```
/                           → Landing page (public) / Dashboard (auth)
/clubs                      → Browse/discover clubs
/clubs/new                  → Create new club
/clubs/{slug}               → Club dashboard
/clubs/{slug}/members       → Club members list
/clubs/{slug}/watchlist     → Club watchlist
/clubs/{slug}/events        → Club events
/clubs/{slug}/events/{id}   → Event details
/clubs/{slug}/discussions   → Club discussions
/clubs/{slug}/discussions/{id} → Discussion thread
/clubs/{slug}/settings      → Club settings (admin)

/movies                     → Movie search/browse
/movies/{imdb_id}           → Movie details page

/watchlist                  → Personal watchlist
/ratings                    → Personal ratings history

/settings                   → User settings (existing)
/settings/profile           → Extended profile settings
```

---

## Component Architecture

### New Components

```
components/
├── Movies/
│   ├── MovieCard.tsx           # Poster card with quick actions
│   ├── MovieDetails.tsx        # Full movie info display
│   ├── MovieSearch.tsx         # Search interface
│   ├── MoviePoster.tsx         # Poster with fallback
│   └── RatingDisplay.tsx       # Star rating visualization
│
├── Clubs/
│   ├── ClubCard.tsx            # Club preview card
│   ├── ClubHeader.tsx          # Club page header
│   ├── ClubSidebar.tsx         # Club navigation
│   ├── MemberList.tsx          # Members grid/list
│   ├── MemberCard.tsx          # Individual member
│   └── CreateClubForm.tsx      # Club creation wizard
│
├── Watchlist/
│   ├── WatchlistTable.tsx      # Sortable watchlist
│   ├── WatchlistCard.tsx       # Movie in watchlist
│   ├── VoteButtons.tsx         # Upvote/downvote
│   └── AddToWatchlist.tsx      # Add movie modal
│
├── Ratings/
│   ├── StarRating.tsx          # Interactive stars
│   ├── RatingForm.tsx          # Rate movie form
│   ├── ReviewCard.tsx          # Review display
│   └── ReviewForm.tsx          # Write review form
│
├── Events/
│   ├── EventCard.tsx           # Event preview
│   ├── EventDetails.tsx        # Full event view
│   ├── EventForm.tsx           # Create/edit event
│   ├── RSVPButtons.tsx         # RSVP actions
│   └── EventCalendar.tsx       # Calendar view
│
├── Discussions/
│   ├── DiscussionList.tsx      # Discussion feed
│   ├── DiscussionThread.tsx    # Thread view
│   ├── ReplyTree.tsx           # Nested replies
│   └── DiscussionForm.tsx      # New discussion/reply
│
└── ArtDeco/                    # Themed UI components
    ├── DecoCard.tsx            # Art deco styled card
    ├── DecoButton.tsx          # Styled button variants
    ├── DecoBorder.tsx          # Decorative borders
    ├── DecoHeader.tsx          # Page headers
    └── FilmStrip.tsx           # Decorative element
```

---

## Security Considerations

### Club Access Control

- Validate club membership on all club-specific endpoints
- Role-based permissions (owner > admin > member)
- Private club data only visible to members
- Invite links with expiration and usage limits

### Rate Limiting

- OMDB API: Max 1 request/second, 1000/day
- User actions: Prevent spam (votes, reviews)
- Search: Debounce and cache common queries

### Data Privacy

- User can control profile visibility
- Option to hide ratings/reviews from public
- GDPR-compliant data export/deletion

---

## Performance Optimizations

### Caching Strategy

1. **OMDB Responses**: PostgreSQL with 30-day TTL
2. **Movie Posters**: Consider image CDN/proxy
3. **Club Data**: React Query with stale-while-revalidate
4. **Search Results**: Cache common searches

### Database Indexes

```sql
-- High-priority indexes
CREATE INDEX idx_movie_imdb_id ON movie(imdb_id);
CREATE INDEX idx_club_slug ON club(slug);
CREATE INDEX idx_membership_user_club ON club_membership(user_id, club_id);
CREATE INDEX idx_watchlist_club_status ON club_watchlist(club_id, status);
CREATE INDEX idx_rating_user_movie ON rating(user_id, movie_id);
CREATE INDEX idx_event_club_start ON event(club_id, start_time);
```

---

## Development Phases

### Phase 1: Foundation (MVP) ✅
- [x] OMDB integration (search, cache, display)
- [x] Movie details page
- [x] Personal watchlist (want to watch, watched)
- [x] Basic star ratings
- [x] Art Deco theme implementation

### Phase 2: Clubs Core ✅
- [x] Club CRUD operations
- [x] Club membership (join, leave, role management)
- [x] Club watchlist with voting
- [x] Basic club dashboard

### Phase 3: Social Features
- [ ] Written reviews with spoiler tags
- [ ] Discussion forums
- [ ] Club activity feed
- [ ] Notifications (in-app)

### Phase 4: Events
- [ ] Event creation and management
- [ ] RSVP system
- [ ] Event calendar view
- [ ] Event reminders (email)

### Phase 5: Polish & Scale
- [ ] Advanced search filters
- [ ] Club discovery/recommendations
- [ ] User achievements/badges
- [ ] Mobile responsiveness refinement
- [ ] Performance optimization

---

## Tech Stack Summary

### Backend (Existing + Extended)
- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: PostgreSQL
- **Auth**: JWT (existing)
- **External API**: OMDB (new)
- **Task Queue**: (Future) Celery for notifications

### Frontend (Existing + Extended)
- **Framework**: React 19 + TypeScript
- **Routing**: TanStack Router
- **State**: TanStack Query
- **Styling**: Tailwind CSS + Custom Art Deco theme
- **Components**: shadcn/ui (customized)
- **Forms**: react-hook-form + Zod

### Infrastructure (Existing)
- **Container**: Docker Compose
- **Proxy**: Traefik
- **Email**: SMTP (Mailcatcher for dev)

---

## Success Metrics

- User registration and retention rates
- Clubs created per week
- Movies added to watchlists
- Ratings and reviews submitted
- Event attendance rates
- Daily/weekly active users
- API response times (< 200ms p95)

---

## Open Questions

1. **Monetization**: Free tier limits? Premium features?
2. **Streaming Integration**: Link to where movies are available?
3. **Mobile App**: PWA sufficient or native apps needed?
4. **Moderation**: How to handle inappropriate content?
5. **Analytics**: What user behavior to track?

---

*Document Version: 1.0*
*Last Updated: February 2026*
*Author: Vantage Development Team*
