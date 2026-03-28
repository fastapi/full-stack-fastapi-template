import { createFileRoute, Link } from "@tanstack/react-router"
import { Calendar, MapPin, Users } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export const Route = createFileRoute("/_public/races")({
  component: RacesPage,
  head: () => ({
    meta: [
      {
        title: "Browse Races - RaceHub",
        description:
          "Find and register for upcoming running races near you. Filter by distance, date, and location.",
      },
    ],
  }),
})

// Placeholder data - will be replaced with API data
const upcomingRaces = [
  {
    id: "1",
    name: "Spring Marathon 2026",
    date: "April 15, 2026",
    location: "Central Park, New York",
    distance: "Marathon",
    participants: 2500,
    description:
      "Join us for the annual Spring Marathon through beautiful Central Park.",
  },
  {
    id: "2",
    name: "City 10K Challenge",
    date: "May 8, 2026",
    location: "Downtown, San Francisco",
    distance: "10K",
    participants: 1200,
    description: "A fast and flat 10K course through the heart of the city.",
  },
  {
    id: "3",
    name: "Trail Half Marathon",
    date: "June 20, 2026",
    location: "Mountain View Trail, Colorado",
    distance: "Half Marathon",
    participants: 800,
    description:
      "Experience stunning mountain views on this challenging trail race.",
  },
]

function RacesPage() {
  return (
    <div className="w-full py-8 md:py-12">
      <div className="container">
        <div className="mx-auto max-w-7xl space-y-8">
          {/* Header */}
          <div className="space-y-4">
            <h1 className="text-3xl font-bold tracking-tight md:text-4xl">
              Upcoming Races
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl">
              Browse and register for upcoming races. Find the perfect event
              that matches your goals and fitness level.
            </p>
          </div>

          {/* Filters - Placeholder */}
          <div className="rounded-lg border bg-muted/50 p-4">
            <p className="text-sm text-muted-foreground">
              Filters coming soon: Distance, Date, Location
            </p>
          </div>

          {/* Races Grid */}
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {upcomingRaces.map((race) => (
              <Card
                key={race.id}
                className="flex flex-col transition-shadow hover:shadow-lg"
              >
                <CardHeader className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Badge variant="outline">{race.distance}</Badge>
                  </div>
                  <CardTitle className="text-xl">{race.name}</CardTitle>
                  <CardDescription>{race.description}</CardDescription>
                </CardHeader>
                <CardContent className="flex-1 space-y-3">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Calendar className="size-4 shrink-0" />
                    <span>{race.date}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <MapPin className="size-4 shrink-0" />
                    <span>{race.location}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Users className="size-4 shrink-0" />
                    <span>{race.participants} registered</span>
                  </div>
                </CardContent>
                <CardFooter>
                  <Button className="w-full" asChild>
                    <Link to="/login">Register Now</Link>
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>

          {/* Empty State */}
          {upcomingRaces.length === 0 && (
            <div className="py-12 text-center">
              <p className="text-lg text-muted-foreground">
                No races found. Check back soon!
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default RacesPage
