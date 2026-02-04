"""OMDB API Integration Service"""

from datetime import datetime, timedelta

import httpx
from sqlmodel import Session, select

from app.core.config import settings
from app.models import Movie, MovieSearchResult, get_datetime_utc


class OMDBError(Exception):
    """Custom exception for OMDB API errors"""

    pass


class OMDBService:
    """Service for interacting with the OMDB API with caching"""

    def __init__(self) -> None:
        self.api_key = settings.OMDB_API_KEY
        self.base_url = settings.OMDB_BASE_URL
        self.cache_ttl_days = settings.OMDB_CACHE_TTL_DAYS

        if not self.api_key:
            raise OMDBError("OMDB_API_KEY not configured")

    async def search_movies(
        self,
        *,
        query: str,
        year: str | None = None,
        type: str | None = None,
        page: int = 1,
    ) -> tuple[list[MovieSearchResult], int]:
        """
        Search OMDB for movies by title.
        Returns tuple of (results, total_results)
        """
        params: dict[str, str | int] = {
            "apikey": self.api_key,  # type: ignore
            "s": query,
            "page": page,
        }
        if year:
            params["y"] = year
        if type:
            params["type"] = type

        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

        if data.get("Response") == "False":
            error = data.get("Error", "Unknown error")
            if error == "Movie not found!":
                return [], 0
            raise OMDBError(error)

        results = []
        for item in data.get("Search", []):
            poster = item.get("Poster")
            results.append(
                MovieSearchResult(
                    imdb_id=item.get("imdbID", ""),
                    title=item.get("Title", ""),
                    year=item.get("Year"),
                    poster_url=poster if poster and poster != "N/A" else None,
                    type=item.get("Type"),
                )
            )

        total_results = int(data.get("totalResults", 0))
        return results, total_results

    async def fetch_movie_details(self, *, imdb_id: str) -> dict:
        """Fetch full movie details from OMDB by IMDB ID"""
        params = {
            "apikey": self.api_key,
            "i": imdb_id,
            "plot": "full",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

        if data.get("Response") == "False":
            raise OMDBError(data.get("Error", "Movie not found"))

        return data

    def _clean_omdb_value(self, value: str | None) -> str | None:
        """Return None for N/A values from OMDB"""
        if value is None or value == "N/A":
            return None
        return value

    def _parse_omdb_response(self, data: dict) -> Movie:
        """Parse OMDB response into Movie model"""
        return Movie(
            imdb_id=data.get("imdbID", ""),
            title=data.get("Title", ""),
            year=self._clean_omdb_value(data.get("Year")),
            rated=self._clean_omdb_value(data.get("Rated")),
            released=self._clean_omdb_value(data.get("Released")),
            runtime=self._clean_omdb_value(data.get("Runtime")),
            genre=self._clean_omdb_value(data.get("Genre")),
            director=self._clean_omdb_value(data.get("Director")),
            writer=self._clean_omdb_value(data.get("Writer")),
            actors=self._clean_omdb_value(data.get("Actors")),
            plot=self._clean_omdb_value(data.get("Plot")),
            language=self._clean_omdb_value(data.get("Language")),
            country=self._clean_omdb_value(data.get("Country")),
            awards=self._clean_omdb_value(data.get("Awards")),
            poster_url=self._clean_omdb_value(data.get("Poster")),
            imdb_rating=self._clean_omdb_value(data.get("imdbRating")),
            imdb_votes=self._clean_omdb_value(data.get("imdbVotes")),
            box_office=self._clean_omdb_value(data.get("BoxOffice")),
            fetched_at=get_datetime_utc(),
            raw_data=data,
        )

    def _is_cache_stale(self, movie: Movie) -> bool:
        """Check if cached movie data is stale"""
        if movie.fetched_at is None:
            return True
        expiry = movie.fetched_at + timedelta(days=self.cache_ttl_days)
        return datetime.now(movie.fetched_at.tzinfo) > expiry

    async def get_or_fetch_movie(
        self,
        *,
        session: Session,
        imdb_id: str,
        force_refresh: bool = False,
    ) -> Movie:
        """
        Get movie from cache or fetch from OMDB.
        Refreshes if cache is stale or force_refresh is True.
        """
        # Check cache first
        statement = select(Movie).where(Movie.imdb_id == imdb_id)
        cached_movie = session.exec(statement).first()

        if cached_movie and not force_refresh and not self._is_cache_stale(cached_movie):
            return cached_movie

        # Fetch from OMDB
        data = await self.fetch_movie_details(imdb_id=imdb_id)

        if cached_movie:
            # Update existing cache
            movie_data = self._parse_omdb_response(data)
            update_dict = movie_data.model_dump(exclude={"id"})
            cached_movie.sqlmodel_update(update_dict)
            session.add(cached_movie)
            session.commit()
            session.refresh(cached_movie)
            return cached_movie
        else:
            # Create new cache entry
            new_movie = self._parse_omdb_response(data)
            session.add(new_movie)
            session.commit()
            session.refresh(new_movie)
            return new_movie


def get_omdb_service() -> OMDBService:
    """Factory function to create OMDB service instance"""
    return OMDBService()
