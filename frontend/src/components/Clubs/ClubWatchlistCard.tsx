import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Link as RouterLink } from "@tanstack/react-router"
import { Trash2 } from "lucide-react"

import type { ClubWatchlistWithMovie } from "@/client"
import { ClubsService } from "@/client"
import { MoviePoster } from "@/components/Movies/MoviePoster"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import { VoteButtons } from "./VoteButtons"

interface ClubWatchlistCardProps {
  clubId: string
  entry: ClubWatchlistWithMovie
  canRemove: boolean
}

export function ClubWatchlistCard({
  clubId,
  entry,
  canRemove,
}: ClubWatchlistCardProps) {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const voteMutation = useMutation({
    mutationFn: (voteType: "upvote" | "downvote") =>
      ClubsService.voteOnWatchlistEntry({
        clubId,
        entryId: entry.id,
        voteType,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clubs", clubId, "watchlist"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const removeMutation = useMutation({
    mutationFn: () =>
      ClubsService.removeFromClubWatchlist({
        clubId,
        entryId: entry.id,
      }),
    onSuccess: () => {
      showSuccessToast("Removed from watchlist")
      queryClient.invalidateQueries({ queryKey: ["clubs", clubId, "watchlist"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const canDelete = canRemove || entry.added_by_user_id === user?.id

  return (
    <Card className="overflow-hidden">
      <div className="flex">
        <RouterLink
          to="/movies/$imdbId"
          params={{ imdbId: entry.movie.imdb_id }}
          className="shrink-0"
        >
          <div className="w-24 h-36">
            <MoviePoster
              posterUrl={entry.movie.poster_url}
              title={entry.movie.title}
              className="w-full h-full object-cover"
            />
          </div>
        </RouterLink>
        <CardContent className="flex-1 p-4 flex flex-col justify-between">
          <div>
            <RouterLink
              to="/movies/$imdbId"
              params={{ imdbId: entry.movie.imdb_id }}
            >
              <h3 className="font-semibold line-clamp-1 hover:text-primary transition-colors">
                {entry.movie.title}
              </h3>
            </RouterLink>
            <p className="text-sm text-muted-foreground">{entry.movie.year}</p>
            {entry.notes && (
              <p className="text-sm text-muted-foreground mt-2 line-clamp-2">
                {entry.notes}
              </p>
            )}
          </div>
          <div className="flex items-center justify-between mt-3">
            <VoteButtons
              upvotes={entry.upvotes ?? 0}
              downvotes={entry.downvotes ?? 0}
              userVote={entry.user_vote ?? null}
              onVote={(voteType) => voteMutation.mutate(voteType)}
              disabled={voteMutation.isPending}
            />
            {canDelete && (
              <Button
                variant="ghost"
                size="icon"
                className="text-muted-foreground hover:text-destructive"
                onClick={() => removeMutation.mutate()}
                disabled={removeMutation.isPending}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>
        </CardContent>
      </div>
    </Card>
  )
}
