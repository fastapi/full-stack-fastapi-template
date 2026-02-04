import { useQuery } from "@tanstack/react-query"
import { createFileRoute, Link as RouterLink } from "@tanstack/react-router"
import { ArrowRight, Users2 } from "lucide-react"

import { ClubsService } from "@/client"
import { ClubCard, CreateClubDialog } from "@/components/Clubs"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: "Dashboard - Vantage",
      },
    ],
  }),
})

function ClubsSection() {
  const { data: clubs, isLoading } = useQuery({
    queryKey: ["clubs"],
    queryFn: () => ClubsService.listClubs({ limit: 3 }),
  })

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-40" />
        ))}
      </div>
    )
  }

  if (!clubs || clubs.count === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-8 bg-muted/30 rounded-lg">
        <div className="rounded-full bg-muted p-3 mb-3">
          <Users2 className="h-6 w-6 text-muted-foreground" />
        </div>
        <h3 className="font-semibold">Start Your Movie Journey</h3>
        <p className="text-sm text-muted-foreground mb-4 max-w-md">
          Create a club to watch and discuss movies with friends
        </p>
        <CreateClubDialog />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {clubs.data.map((club) => (
          <ClubCard key={club.id} club={club} />
        ))}
      </div>
      {clubs.count > 3 && (
        <div className="flex justify-center">
          <Button variant="outline" asChild>
            <RouterLink to="/clubs">
              View All Clubs
              <ArrowRight className="h-4 w-4 ml-2" />
            </RouterLink>
          </Button>
        </div>
      )}
    </div>
  )
}

function Dashboard() {
  const { user: currentUser } = useAuth()

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl truncate max-w-sm">
          Hi, {currentUser?.full_name || currentUser?.email} 👋
        </h1>
        <p className="text-muted-foreground">
          Welcome back, nice to see you again!
        </p>
      </div>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">My Clubs</h2>
            <p className="text-sm text-muted-foreground">
              Your movie clubs and communities
            </p>
          </div>
          <Button variant="ghost" asChild>
            <RouterLink to="/clubs">
              See All
              <ArrowRight className="h-4 w-4 ml-2" />
            </RouterLink>
          </Button>
        </div>
        <ClubsSection />
      </section>
    </div>
  )
}
