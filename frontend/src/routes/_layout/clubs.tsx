import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Users2 } from "lucide-react"

import { ClubsService } from "@/client"
import { ClubCard, CreateClubDialog } from "@/components/Clubs"
import { Skeleton } from "@/components/ui/skeleton"

export const Route = createFileRoute("/_layout/clubs")({
  component: Clubs,
  head: () => ({
    meta: [
      {
        title: "My Clubs - Vantage",
      },
    ],
  }),
})

function ClubsLoading() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="space-y-3">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
        </div>
      ))}
    </div>
  )
}

function ClubsEmpty() {
  return (
    <div className="flex flex-col items-center justify-center text-center py-16">
      <div className="rounded-full bg-muted p-4 mb-4">
        <Users2 className="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 className="text-lg font-semibold">No clubs yet</h3>
      <p className="text-muted-foreground mb-6 max-w-md">
        Create a club to start watching and discussing movies with friends, or
        join a public club to meet new movie enthusiasts.
      </p>
      <CreateClubDialog />
    </div>
  )
}

function Clubs() {
  const { data: clubs, isLoading, isError } = useQuery({
    queryKey: ["clubs"],
    queryFn: () => ClubsService.listClubs({}),
  })

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">My Clubs</h1>
          <p className="text-muted-foreground">
            Join or create movie clubs to watch together
          </p>
        </div>
        {clubs && clubs.count > 0 && <CreateClubDialog />}
      </div>

      {isLoading && <ClubsLoading />}

      {isError && (
        <div className="text-center py-12">
          <p className="text-destructive">Failed to load clubs</p>
        </div>
      )}

      {clubs && clubs.count === 0 && <ClubsEmpty />}

      {clubs && clubs.count > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {clubs.data.map((club) => (
            <ClubCard key={club.id} club={club} />
          ))}
        </div>
      )}
    </div>
  )
}
