import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, Link as RouterLink } from "@tanstack/react-router"
import {
  ArrowLeft,
  Calendar,
  Clock,
  Globe,
  Plus,
  Star,
  Trophy,
  Users,
} from "lucide-react"
import { useState } from "react"

import { MoviesService, RatingsService, WatchlistService } from "@/client"
import { MoviePoster } from "@/components/Movies/MoviePoster"
import { StarRating } from "@/components/Ratings/StarRating"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import useCustomToast from "@/hooks/useCustomToast"

export const Route = createFileRoute("/_layout/movies/$imdbId")({
  component: MovieDetails,
})

function MovieDetailsSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-8 w-32" />
      <div className="grid md:grid-cols-[300px_1fr] gap-8">
        <Skeleton className="aspect-[2/3] w-full" />
        <div className="space-y-4">
          <Skeleton className="h-10 w-3/4" />
          <Skeleton className="h-6 w-1/2" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-32 w-full" />
        </div>
      </div>
    </div>
  )
}

function MovieDetails() {
  const { imdbId } = Route.useParams()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [userRating, setUserRating] = useState<number>(0)

  const {
    data: movie,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["movies", imdbId],
    queryFn: () => MoviesService.getMovie({ imdbId }),
  })

  const { data: ratingStats } = useQuery({
    queryKey: ["movies", imdbId, "ratings"],
    queryFn: () => MoviesService.getMovieRatings({ imdbId }),
    enabled: !!movie,
  })

  const addToWatchlistMutation = useMutation({
    mutationFn: () =>
      WatchlistService.addToWatchlist({
        requestBody: { movie_imdb_id: imdbId, status: "want_to_watch" },
      }),
    onSuccess: () => {
      showSuccessToast("Added to watchlist!")
      queryClient.invalidateQueries({ queryKey: ["watchlist"] })
    },
    onError: (error: Error) => {
      if (error.message.includes("already")) {
        showErrorToast("Movie already in watchlist")
      } else {
        showErrorToast("Failed to add to watchlist")
      }
    },
  })

  const rateMutation = useMutation({
    mutationFn: (score: number) =>
      RatingsService.createRating({
        requestBody: { movie_imdb_id: imdbId, score },
      }),
    onSuccess: () => {
      showSuccessToast("Rating saved!")
      queryClient.invalidateQueries({ queryKey: ["movies", imdbId, "ratings"] })
      queryClient.invalidateQueries({ queryKey: ["ratings"] })
    },
    onError: () => showErrorToast("Failed to save rating"),
  })

  const handleRate = (rating: number) => {
    setUserRating(rating)
    rateMutation.mutate(rating)
  }

  if (isLoading) {
    return <MovieDetailsSkeleton />
  }

  if (isError || !movie) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive">Failed to load movie details</p>
        <RouterLink to="/movies">
          <Button variant="outline" className="mt-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Search
          </Button>
        </RouterLink>
      </div>
    )
  }

  const genres = movie.genre?.split(", ") || []

  return (
    <div className="space-y-8">
      {/* Back button */}
      <RouterLink to="/movies">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Search
        </Button>
      </RouterLink>

      {/* Hero section */}
      <div className="grid md:grid-cols-[300px_1fr] gap-8">
        {/* Poster and Actions */}
        <div className="space-y-4">
          <MoviePoster
            posterUrl={movie.poster_url}
            title={movie.title}
            className="w-full shadow-lg"
          />
          <Button
            className="w-full"
            onClick={() => addToWatchlistMutation.mutate()}
            disabled={addToWatchlistMutation.isPending}
          >
            <Plus className="h-4 w-4 mr-2" />
            Add to Watchlist
          </Button>
        </div>

        {/* Movie Info */}
        <div className="space-y-6">
          {/* Title and Genres */}
          <div>
            <h1 className="text-3xl font-bold font-display">{movie.title}</h1>
            {genres.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3">
                {genres.map((genre) => (
                  <Badge key={genre} variant="secondary">
                    {genre}
                  </Badge>
                ))}
              </div>
            )}
          </div>

          {/* Meta info */}
          <div className="flex flex-wrap gap-6 text-sm text-muted-foreground">
            {movie.year && (
              <div className="flex items-center gap-1.5">
                <Calendar className="h-4 w-4" />
                <span>{movie.year}</span>
              </div>
            )}
            {movie.runtime && (
              <div className="flex items-center gap-1.5">
                <Clock className="h-4 w-4" />
                <span>{movie.runtime}</span>
              </div>
            )}
            {movie.rated && <Badge variant="outline">{movie.rated}</Badge>}
            {movie.language && (
              <div className="flex items-center gap-1.5">
                <Globe className="h-4 w-4" />
                <span>{movie.language}</span>
              </div>
            )}
          </div>

          {/* Plot */}
          {movie.plot && (
            <div>
              <h2 className="font-display font-semibold text-lg mb-2">Plot</h2>
              <p className="text-muted-foreground leading-relaxed">
                {movie.plot}
              </p>
            </div>
          )}

          {/* Awards */}
          {movie.awards && movie.awards !== "N/A" && (
            <div className="flex items-start gap-2 text-sm">
              <Trophy className="h-4 w-4 text-[var(--gold)] mt-0.5" />
              <span className="text-muted-foreground">{movie.awards}</span>
            </div>
          )}

          {/* Rating Card */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-lg">
                <Star className="h-5 w-5 text-[var(--gold)]" />
                Ratings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* IMDB Rating */}
              {movie.imdb_rating && (
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">IMDB</span>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">{movie.imdb_rating}/10</span>
                    <span className="text-xs text-muted-foreground">
                      ({movie.imdb_votes} votes)
                    </span>
                  </div>
                </div>
              )}

              {/* Vantage Community Rating */}
              {ratingStats && ratingStats.rating_count > 0 && (
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium flex items-center gap-1.5">
                    <Users className="h-4 w-4" />
                    Vantage
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">
                      {ratingStats.average_rating.toFixed(1)}/5
                    </span>
                    <span className="text-xs text-muted-foreground">
                      ({ratingStats.rating_count} ratings)
                    </span>
                  </div>
                </div>
              )}

              {/* User Rating */}
              <div className="pt-3 border-t">
                <p className="text-sm font-medium mb-2">Your Rating</p>
                <StarRating value={userRating} onChange={handleRate} size="lg" />
              </div>
            </CardContent>
          </Card>

          {/* Credits */}
          <div className="grid md:grid-cols-2 gap-6">
            {movie.director && (
              <div>
                <h3 className="font-display font-semibold mb-1">Director</h3>
                <p className="text-muted-foreground">{movie.director}</p>
              </div>
            )}
            {movie.writer && (
              <div>
                <h3 className="font-display font-semibold mb-1">Writer</h3>
                <p className="text-muted-foreground">{movie.writer}</p>
              </div>
            )}
            {movie.actors && (
              <div className="md:col-span-2">
                <h3 className="font-display font-semibold mb-1">Cast</h3>
                <p className="text-muted-foreground">{movie.actors}</p>
              </div>
            )}
          </div>

          {/* Additional Info */}
          {movie.box_office && (
            <div>
              <h3 className="font-display font-semibold mb-1">Box Office</h3>
              <p className="text-muted-foreground">{movie.box_office}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
