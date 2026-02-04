import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Plus, Search } from "lucide-react"
import { useState } from "react"
import { useDebouncedCallback } from "use-debounce"

import type { MovieSearchResult } from "@/client"
import { ClubsService, MoviesService } from "@/client"
import { MoviePoster } from "@/components/Movies/MoviePoster"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface AddMovieToClubDialogProps {
  clubId: string
}

export function AddMovieToClubDialog({ clubId }: AddMovieToClubDialogProps) {
  const [open, setOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [debouncedQuery, setDebouncedQuery] = useState("")
  const [selectedMovie, setSelectedMovie] = useState<MovieSearchResult | null>(
    null
  )
  const [notes, setNotes] = useState("")
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const handleSearch = useDebouncedCallback((value: string) => {
    setDebouncedQuery(value)
  }, 300)

  const { data: searchResults, isLoading } = useQuery({
    queryKey: ["movies", "search", debouncedQuery],
    queryFn: () => MoviesService.searchMovies({ q: debouncedQuery }),
    enabled: debouncedQuery.length >= 2,
  })

  const addMovieMutation = useMutation({
    mutationFn: () =>
      ClubsService.addToClubWatchlist({
        clubId,
        requestBody: {
          movie_imdb_id: selectedMovie!.imdb_id,
          notes: notes || undefined,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Movie added to watchlist!")
      queryClient.invalidateQueries({ queryKey: ["clubs", clubId, "watchlist"] })
      setOpen(false)
      setSelectedMovie(null)
      setNotes("")
      setSearchQuery("")
      setDebouncedQuery("")
    },
    onError: handleError.bind(showErrorToast),
  })

  const handleSelectMovie = (movie: MovieSearchResult) => {
    setSelectedMovie(movie)
  }

  const handleBack = () => {
    setSelectedMovie(null)
    setNotes("")
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Movie
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px] max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {selectedMovie ? "Add to Watchlist" : "Search Movies"}
          </DialogTitle>
          <DialogDescription>
            {selectedMovie
              ? "Add a note for the club (optional)"
              : "Search for a movie to add to the club's watchlist"}
          </DialogDescription>
        </DialogHeader>

        {selectedMovie ? (
          <div className="space-y-4">
            <div className="flex gap-4">
              <div className="w-20 h-28 shrink-0">
                <MoviePoster
                  posterUrl={selectedMovie.poster_url}
                  title={selectedMovie.title}
                  className="w-full h-full object-cover rounded"
                />
              </div>
              <div>
                <h3 className="font-semibold">{selectedMovie.title}</h3>
                <p className="text-sm text-muted-foreground">
                  {selectedMovie.year}
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Note (Optional)</label>
              <Textarea
                placeholder="Why should the club watch this?"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="resize-none"
              />
            </div>

            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={handleBack}>
                Back
              </Button>
              <Button
                onClick={() => addMovieMutation.mutate()}
                disabled={addMovieMutation.isPending}
              >
                Add to Watchlist
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search for movies..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value)
                  handleSearch(e.target.value)
                }}
              />
            </div>

            {isLoading && (
              <div className="space-y-2">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="flex gap-3 p-2">
                    <Skeleton className="w-12 h-16" />
                    <div className="space-y-2 flex-1">
                      <Skeleton className="h-4 w-3/4" />
                      <Skeleton className="h-3 w-1/4" />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {searchResults && searchResults.data.length > 0 && (
              <div className="space-y-1 max-h-[300px] overflow-y-auto">
                {searchResults.data.map((movie) => (
                  <button
                    key={movie.imdb_id}
                    className="flex gap-3 p-2 w-full hover:bg-muted rounded-lg transition-colors text-left"
                    onClick={() => handleSelectMovie(movie)}
                  >
                    <div className="w-12 h-16 shrink-0">
                      <MoviePoster
                        posterUrl={movie.poster_url}
                        title={movie.title}
                        className="w-full h-full object-cover rounded"
                      />
                    </div>
                    <div>
                      <p className="font-medium line-clamp-1">{movie.title}</p>
                      <p className="text-sm text-muted-foreground">
                        {movie.year}
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {debouncedQuery.length >= 2 &&
              !isLoading &&
              searchResults?.data.length === 0 && (
                <p className="text-center text-muted-foreground py-4">
                  No movies found
                </p>
              )}

            {debouncedQuery.length < 2 && (
              <p className="text-center text-muted-foreground py-4">
                Enter at least 2 characters to search
              </p>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
