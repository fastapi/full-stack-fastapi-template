import { createFileRoute } from "@tanstack/react-router"
import { useQuery } from "@tanstack/react-query"
import { ProfilesService } from "@/client"
import { RaceCard } from "@/components/Races/RaceCard"
import { SaveButton } from "@/components/Races/SaveButton"
import { Skeleton } from "@/components/ui/skeleton"
import { Bookmark } from "lucide-react"
import { Link } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/saved")({
  component: SavedRacesPage,
  head: () => ({
    meta: [{ title: "Saved Races - VNRunner" }],
  }),
})

function SavedRacesPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["savedRaces"],
    queryFn: () => ProfilesService.getMySavedRaces(),
  })

  const races = data?.data ?? []

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight">Saved Races</h1>
        <p className="text-muted-foreground">Races you've bookmarked for later.</p>
      </div>

      {isLoading ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-64 rounded-lg" />
          ))}
        </div>
      ) : races.length === 0 ? (
        <div className="py-16 text-center space-y-3">
          <Bookmark className="mx-auto size-10 text-muted-foreground/50" />
          <p className="text-lg font-medium">No saved races yet</p>
          <p className="text-sm text-muted-foreground">
            Browse races and click the bookmark icon to save them here.
          </p>
          <Link
            to="/races"
            className="mt-2 inline-flex items-center gap-1 text-sm text-primary hover:underline"
          >
            Browse races →
          </Link>
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {races.map((race) => (
            <div key={race.id} className="relative">
              <RaceCard race={race} />
              <div className="absolute right-3 top-3">
                <SaveButton raceId={race.id} isSaved />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
