import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, Link as RouterLink } from "@tanstack/react-router"
import { MoreHorizontal, Search, Star, Trash2 } from "lucide-react"

import { RatingsService } from "@/client"
import type { RatingWithMovie } from "@/client"
import { MoviePoster } from "@/components/Movies/MoviePoster"
import { StarRating } from "@/components/Ratings/StarRating"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Skeleton } from "@/components/ui/skeleton"
import useCustomToast from "@/hooks/useCustomToast"

export const Route = createFileRoute("/_layout/ratings")({
  component: Ratings,
})

function RatingsSkeleton() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex gap-4 p-4 border rounded-lg">
          <Skeleton className="w-16 h-24 rounded" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-5 w-1/2" />
            <Skeleton className="h-4 w-1/4" />
            <Skeleton className="h-5 w-32" />
          </div>
        </div>
      ))}
    </div>
  )
}

function EmptyState() {
  return (
    <div className="text-center py-12">
      <Star className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
      <p className="text-muted-foreground mb-4">
        You haven't rated any movies yet
      </p>
      <RouterLink to="/movies">
        <Button>
          <Search className="h-4 w-4 mr-2" />
          Discover Movies
        </Button>
      </RouterLink>
    </div>
  )
}

function RatingEntry({
  rating,
  onUpdate,
  onDelete,
}: {
  rating: RatingWithMovie
  onUpdate: (id: string, score: number) => void
  onDelete: (id: string) => void
}) {
  return (
    <div className="flex items-center gap-4 p-4 border rounded-lg hover:bg-muted/50 transition-colors">
      <RouterLink
        to="/movies/$imdbId"
        params={{ imdbId: rating.movie.imdb_id }}
        className="shrink-0"
      >
        <MoviePoster
          posterUrl={rating.movie.poster_url}
          title={rating.movie.title}
          className="w-16 h-24 object-cover"
        />
      </RouterLink>
      <div className="flex-1 min-w-0">
        <RouterLink
          to="/movies/$imdbId"
          params={{ imdbId: rating.movie.imdb_id }}
        >
          <h3 className="font-semibold hover:text-primary transition-colors line-clamp-1">
            {rating.movie.title}
          </h3>
        </RouterLink>
        <p className="text-sm text-muted-foreground">{rating.movie.year}</p>
        <div className="mt-2">
          <StarRating
            value={rating.score}
            onChange={(score) => onUpdate(rating.id, score)}
            size="sm"
          />
        </div>
        <p className="text-xs text-muted-foreground mt-1">
          Rated on {new Date(rating.updated_at).toLocaleDateString()}
        </p>
      </div>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem
            className="text-destructive focus:text-destructive"
            onClick={() => onDelete(rating.id)}
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Delete Rating
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}

function Ratings() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const {
    data: ratings,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["ratings", "me"],
    queryFn: () => RatingsService.getMyRatings({}),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, score }: { id: string; score: number }) =>
      RatingsService.updateRating({
        ratingId: id,
        requestBody: { score },
      }),
    onSuccess: () => {
      showSuccessToast("Rating updated!")
      queryClient.invalidateQueries({ queryKey: ["ratings"] })
    },
    onError: () => showErrorToast("Failed to update rating"),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => RatingsService.deleteRating({ ratingId: id }),
    onSuccess: () => {
      showSuccessToast("Rating deleted")
      queryClient.invalidateQueries({ queryKey: ["ratings"] })
    },
    onError: () => showErrorToast("Failed to delete rating"),
  })

  const handleUpdate = (id: string, score: number) => {
    updateMutation.mutate({ id, score })
  }

  const handleDelete = (id: string) => {
    deleteMutation.mutate(id)
  }

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight font-display">
            My Ratings
          </h1>
          <p className="text-muted-foreground">
            All the movies you've rated
          </p>
        </div>
        <RatingsSkeleton />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive">Failed to load ratings</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight font-display">
          My Ratings
        </h1>
        <p className="text-muted-foreground">
          All the movies you've rated ({ratings?.count || 0} total)
        </p>
      </div>

      {!ratings || ratings.data.length === 0 ? (
        <EmptyState />
      ) : (
        <div className="space-y-4">
          {ratings.data.map((rating) => (
            <RatingEntry
              key={rating.id}
              rating={rating}
              onUpdate={handleUpdate}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  )
}
