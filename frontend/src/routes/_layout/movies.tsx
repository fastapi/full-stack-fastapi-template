import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Film, Search } from "lucide-react"
import { useState } from "react"
import { useDebouncedCallback } from "use-debounce"

import { MoviesService, WatchlistService } from "@/client"
import type { MovieSearchResult } from "@/client"
import { MovieCard } from "@/components/Movies/MovieCard"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import useCustomToast from "@/hooks/useCustomToast"

export const Route = createFileRoute("/_layout/movies")({
  component: Movies,
})

function MovieSearchResults({
  query,
  onAddToWatchlist,
}: {
  query: string
  onAddToWatchlist: (movie: MovieSearchResult) => void
}) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["movies", "search", query],
    queryFn: () => MoviesService.searchMovies({ q: query }),
    enabled: query.length >= 2,
  })

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
        {Array.from({ length: 10 }).map((_, i) => (
          <div key={i} className="space-y-3">
            <Skeleton className="aspect-[2/3] w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/4" />
          </div>
        ))}
      </div>
    )
  }

  if (isError) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive">Failed to search movies</p>
      </div>
    )
  }

  if (!data || data.data.length === 0) {
    return (
      <div className="text-center py-12">
        <Search className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <p className="text-muted-foreground">No movies found</p>
      </div>
    )
  }

  return (
    <>
      <p className="text-sm text-muted-foreground mb-4">
        Found {data.total_results} results
      </p>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
        {data.data.map((movie) => (
          <MovieCard
            key={movie.imdb_id}
            movie={movie}
            onAddToWatchlist={() => onAddToWatchlist(movie)}
          />
        ))}
      </div>
    </>
  )
}

function Movies() {
  const [searchQuery, setSearchQuery] = useState("")
  const [debouncedQuery, setDebouncedQuery] = useState("")
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const handleSearch = useDebouncedCallback((value: string) => {
    setDebouncedQuery(value)
  }, 300)

  const addToWatchlistMutation = useMutation({
    mutationFn: (imdbId: string) =>
      WatchlistService.addToWatchlist({
        requestBody: { movie_imdb_id: imdbId, status: "want_to_watch" },
      }),
    onSuccess: () => {
      showSuccessToast("Added to watchlist!")
      queryClient.invalidateQueries({ queryKey: ["watchlist"] })
    },
    onError: (error: Error) => {
      if (error.message.includes("already in watchlist")) {
        showErrorToast("Movie already in watchlist")
      } else {
        showErrorToast("Failed to add to watchlist")
      }
    },
  })

  const handleAddToWatchlist = (movie: MovieSearchResult) => {
    addToWatchlistMutation.mutate(movie.imdb_id)
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight font-display">
          Discover Movies
        </h1>
        <p className="text-muted-foreground">
          Search our extensive movie database powered by OMDB
        </p>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search for movies, series..."
          className="pl-10"
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value)
            handleSearch(e.target.value)
          }}
        />
      </div>

      {debouncedQuery.length >= 2 ? (
        <MovieSearchResults
          query={debouncedQuery}
          onAddToWatchlist={handleAddToWatchlist}
        />
      ) : (
        <div className="text-center py-16">
          <Film className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-xl font-display font-semibold mb-2">
            Start Your Search
          </h2>
          <p className="text-muted-foreground max-w-md mx-auto">
            Enter at least 2 characters to search for movies, TV series, and
            more from our extensive database.
          </p>
        </div>
      )}
    </div>
  )
}
