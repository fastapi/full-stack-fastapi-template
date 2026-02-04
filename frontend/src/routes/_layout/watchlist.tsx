import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, Link as RouterLink } from "@tanstack/react-router"
import {
  Eye,
  EyeOff,
  Film,
  MoreHorizontal,
  Search,
  Trash2,
} from "lucide-react"

import { WatchlistService } from "@/client"
import type { UserWatchlistWithMovie } from "@/client"
import { MoviePoster } from "@/components/Movies/MoviePoster"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import useCustomToast from "@/hooks/useCustomToast"

export const Route = createFileRoute("/_layout/watchlist")({
  component: Watchlist,
})

function WatchlistSkeleton() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex gap-4 p-4 border rounded-lg">
          <Skeleton className="w-16 h-24 rounded" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-5 w-1/2" />
            <Skeleton className="h-4 w-1/4" />
          </div>
        </div>
      ))}
    </div>
  )
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="text-center py-12">
      <Film className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
      <p className="text-muted-foreground mb-4">{message}</p>
      <RouterLink to="/movies">
        <Button>
          <Search className="h-4 w-4 mr-2" />
          Discover Movies
        </Button>
      </RouterLink>
    </div>
  )
}

function WatchlistEntry({
  entry,
  onUpdate,
  onDelete,
}: {
  entry: UserWatchlistWithMovie
  onUpdate: (id: string, status: string) => void
  onDelete: (id: string) => void
}) {
  return (
    <div className="flex items-center gap-4 p-4 border rounded-lg hover:bg-muted/50 transition-colors">
      <RouterLink
        to="/movies/$imdbId"
        params={{ imdbId: entry.movie.imdb_id }}
        className="shrink-0"
      >
        <MoviePoster
          posterUrl={entry.movie.poster_url}
          title={entry.movie.title}
          className="w-16 h-24 object-cover"
        />
      </RouterLink>
      <div className="flex-1 min-w-0">
        <RouterLink
          to="/movies/$imdbId"
          params={{ imdbId: entry.movie.imdb_id }}
        >
          <h3 className="font-semibold hover:text-primary transition-colors line-clamp-1">
            {entry.movie.title}
          </h3>
        </RouterLink>
        <p className="text-sm text-muted-foreground">{entry.movie.year}</p>
        {entry.notes && (
          <p className="text-sm text-muted-foreground mt-1 line-clamp-1">
            {entry.notes}
          </p>
        )}
        {entry.watched_at && (
          <p className="text-xs text-muted-foreground mt-1">
            Watched on {new Date(entry.watched_at).toLocaleDateString()}
          </p>
        )}
      </div>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          {entry.status === "want_to_watch" ? (
            <DropdownMenuItem onClick={() => onUpdate(entry.id, "watched")}>
              <Eye className="h-4 w-4 mr-2" />
              Mark as Watched
            </DropdownMenuItem>
          ) : (
            <DropdownMenuItem
              onClick={() => onUpdate(entry.id, "want_to_watch")}
            >
              <EyeOff className="h-4 w-4 mr-2" />
              Move to Want to Watch
            </DropdownMenuItem>
          )}
          <DropdownMenuItem
            className="text-destructive focus:text-destructive"
            onClick={() => onDelete(entry.id)}
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Remove
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}

function Watchlist() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const {
    data: watchlist,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["watchlist"],
    queryFn: () => WatchlistService.getMyWatchlist({}),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      WatchlistService.updateWatchlistEntry({
        watchlistId: id,
        requestBody: { status: status as "want_to_watch" | "watched" },
      }),
    onSuccess: () => {
      showSuccessToast("Watchlist updated!")
      queryClient.invalidateQueries({ queryKey: ["watchlist"] })
    },
    onError: () => showErrorToast("Failed to update"),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) =>
      WatchlistService.removeFromWatchlist({ watchlistId: id }),
    onSuccess: () => {
      showSuccessToast("Removed from watchlist")
      queryClient.invalidateQueries({ queryKey: ["watchlist"] })
    },
    onError: () => showErrorToast("Failed to remove"),
  })

  const handleUpdate = (id: string, status: string) => {
    updateMutation.mutate({ id, status })
  }

  const handleDelete = (id: string) => {
    deleteMutation.mutate(id)
  }

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight font-display">
            My Watchlist
          </h1>
          <p className="text-muted-foreground">
            Track movies you want to watch and have watched
          </p>
        </div>
        <WatchlistSkeleton />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive">Failed to load watchlist</p>
      </div>
    )
  }

  const wantToWatch =
    watchlist?.data.filter((e) => e.status === "want_to_watch") || []
  const watched = watchlist?.data.filter((e) => e.status === "watched") || []

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight font-display">
          My Watchlist
        </h1>
        <p className="text-muted-foreground">
          Track movies you want to watch and have watched
        </p>
      </div>

      <Tabs defaultValue="want_to_watch" className="space-y-6">
        <TabsList>
          <TabsTrigger value="want_to_watch">
            Want to Watch ({wantToWatch.length})
          </TabsTrigger>
          <TabsTrigger value="watched">Watched ({watched.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="want_to_watch" className="space-y-4">
          {wantToWatch.length === 0 ? (
            <EmptyState message="No movies in your watch list yet" />
          ) : (
            wantToWatch.map((entry) => (
              <WatchlistEntry
                key={entry.id}
                entry={entry}
                onUpdate={handleUpdate}
                onDelete={handleDelete}
              />
            ))
          )}
        </TabsContent>

        <TabsContent value="watched" className="space-y-4">
          {watched.length === 0 ? (
            <EmptyState message="You haven't watched any movies yet" />
          ) : (
            watched.map((entry) => (
              <WatchlistEntry
                key={entry.id}
                entry={entry}
                onUpdate={handleUpdate}
                onDelete={handleDelete}
              />
            ))
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
