import { Link } from "@tanstack/react-router"
import { Calendar, MapPin, Mountain, TrendingUp, Sparkles } from "lucide-react"
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
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import type { RacePublic } from "@/client"

interface RaceCardProps {
  race: RacePublic & { ai_explanation?: string | null }
  distanceKm?: number
}

const terrainLabels: Record<string, string> = {
  road: "Road",
  trail: "Trail",
  track: "Track",
  mixed: "Mixed",
}

const difficultyColors: Record<string, string> = {
  easy: "bg-green-100 text-green-800",
  moderate: "bg-yellow-100 text-yellow-800",
  hard: "bg-orange-100 text-orange-800",
  extreme: "bg-red-100 text-red-800",
}

export function RaceCard({ race, distanceKm }: RaceCardProps) {
  const aiExplanation = "ai_explanation" in race ? race.ai_explanation : null
  const eventDate = race.event_start_date
    ? new Date(race.event_start_date).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      })
    : null

  const location = [race.city, race.state, race.country].filter(Boolean).join(", ")

  return (
    <Card className="flex flex-col transition-shadow hover:shadow-lg">
      <CardHeader className="space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          {race.terrain_type && (
            <Badge variant="outline">{terrainLabels[race.terrain_type] ?? race.terrain_type}</Badge>
          )}
          {race.difficulty_level && (
            <span
              className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${difficultyColors[race.difficulty_level] ?? ""}`}
            >
              {race.difficulty_level}
            </span>
          )}
          {race.is_certified && (
            <Badge variant="secondary">Certified</Badge>
          )}
          {aiExplanation && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <span className="inline-flex items-center gap-1 rounded-full bg-purple-100 px-2 py-0.5 text-xs font-medium text-purple-700 cursor-help">
                    <Sparkles className="size-3" /> AI Pick
                  </span>
                </TooltipTrigger>
                <TooltipContent className="max-w-xs">
                  <p className="text-sm">{aiExplanation}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}
        </div>
        <CardTitle className="text-xl leading-tight">{race.name}</CardTitle>
        {race.description && (
          <CardDescription className="line-clamp-2">{race.description}</CardDescription>
        )}
      </CardHeader>

      <CardContent className="flex-1 space-y-2">
        {eventDate && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="size-4 shrink-0" />
            <span>{eventDate}</span>
          </div>
        )}
        {location && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <MapPin className="size-4 shrink-0" />
            <span>{location}</span>
          </div>
        )}
        {distanceKm !== undefined && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <TrendingUp className="size-4 shrink-0" />
            <span>{distanceKm.toFixed(1)} km away</span>
          </div>
        )}
        {race.elevation_gain_m != null && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Mountain className="size-4 shrink-0" />
            <span>{race.elevation_gain_m}m elevation gain</span>
          </div>
        )}
      </CardContent>

      <CardFooter>
        <Button className="w-full" asChild>
          <Link to="/login">Register Now</Link>
        </Button>
      </CardFooter>
    </Card>
  )
}
