import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Film } from "lucide-react"

import { ClubsService } from "@/client"
import {
  AddMovieToClubDialog,
  ClubHeader,
  ClubWatchlistCard,
  MemberList,
} from "@/components/Clubs"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/clubs/$clubId")({
  component: ClubDetail,
  head: () => ({
    meta: [
      {
        title: "Club - Vantage",
      },
    ],
  }),
})

function ClubLoading() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-96" />
      </div>
      <Skeleton className="h-48 w-full" />
    </div>
  )
}

function ClubDetail() {
  const { clubId } = Route.useParams()
  const { user } = useAuth()

  const { data: club, isLoading, isError } = useQuery({
    queryKey: ["clubs", clubId],
    queryFn: () => ClubsService.getClub({ clubId }),
  })

  const { data: watchlist, isLoading: watchlistLoading } = useQuery({
    queryKey: ["clubs", clubId, "watchlist"],
    queryFn: () => ClubsService.getClubWatchlist({ clubId }),
    enabled: !!club,
  })

  if (isLoading) {
    return <ClubLoading />
  }

  if (isError || !club) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive">Failed to load club</p>
      </div>
    )
  }

  const currentMember = club.members.find((m) => m.user_id === user?.id)
  const isMember = !!currentMember && currentMember.role !== "pending"
  const isAdmin =
    currentMember?.role === "admin" || currentMember?.role === "owner"

  return (
    <div className="flex flex-col gap-6">
      <ClubHeader club={club} />

      {isMember && (
        <Tabs defaultValue="watchlist">
          <TabsList>
            <TabsTrigger value="watchlist">Watchlist</TabsTrigger>
            <TabsTrigger value="members">Members</TabsTrigger>
          </TabsList>

          <TabsContent value="watchlist" className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Club Watchlist</h2>
              <AddMovieToClubDialog clubId={clubId} />
            </div>

            {watchlistLoading && (
              <div className="space-y-4">
                {Array.from({ length: 3 }).map((_, i) => (
                  <Skeleton key={i} className="h-36 w-full" />
                ))}
              </div>
            )}

            {watchlist && watchlist.count === 0 && (
              <div className="flex flex-col items-center justify-center text-center py-12">
                <div className="rounded-full bg-muted p-4 mb-4">
                  <Film className="h-8 w-8 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-semibold">No movies yet</h3>
                <p className="text-muted-foreground mb-4">
                  Add a movie to get the club started
                </p>
                <AddMovieToClubDialog clubId={clubId} />
              </div>
            )}

            {watchlist && watchlist.count > 0 && (
              <div className="grid gap-4 md:grid-cols-2">
                {watchlist.data.map((entry) => (
                  <ClubWatchlistCard
                    key={entry.id}
                    clubId={clubId}
                    entry={entry}
                    canRemove={isAdmin}
                  />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="members">
            <MemberList
              clubId={clubId}
              members={club.members}
              currentUserRole={currentMember?.role}
            />
          </TabsContent>
        </Tabs>
      )}

      {!isMember && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">
            Join this club to see the watchlist and members.
          </p>
        </div>
      )}
    </div>
  )
}
