import { createFileRoute, Link } from "@tanstack/react-router"
import { useQuery } from "@tanstack/react-query"
import { RacesService } from "@/client"
import type { RacePublicWithDetails } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { RaceCard } from "@/components/Races/RaceCard"
import { useRaceSearch } from "@/hooks/useRaceSearch"
import { cn } from "@/lib/utils"
import { CourseMap } from "@/components/Races/CourseMap"
import { RaceAssistant } from "@/components/Races/RaceAssistant"
import { MapPin, Calendar, Mountain, Globe, Award } from "lucide-react"

export const Route = createFileRoute("/_public/races/$raceId")({
  component: RaceDetailPage,
  head: ({ params }) => ({
    meta: [{ title: `Race Details - VNRunner` }],
  }),
})

const TERRAIN_LABELS: Record<string, string> = {
  road: "Road",
  trail: "Trail",
  track: "Track",
  mixed: "Mixed",
}

const DIFFICULTY_COLORS: Record<string, string> = {
  easy: "bg-green-100 text-green-800",
  moderate: "bg-yellow-100 text-yellow-800",
  hard: "bg-orange-100 text-orange-800",
  extreme: "bg-red-100 text-red-800",
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  })
}

function InfoRow({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center gap-3 py-2">
      <span className="text-muted-foreground">{icon}</span>
      <span className="text-sm text-muted-foreground w-28 shrink-0">{label}</span>
      <span className="text-sm font-medium">{value}</span>
    </div>
  )
}

function RaceDetailSkeleton() {
  return (
    <div className="space-y-8">
      <Skeleton className="h-48 w-full rounded-xl" />
      <div className="space-y-4">
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </div>
    </div>
  )
}

function RaceDetailPage() {
  const { raceId } = Route.useParams()

  const { data: race, isLoading } = useQuery<RacePublicWithDetails>({
    queryKey: ["race", raceId],
    queryFn: () => RacesService.readRace({ raceId }),
  })

  const { data: similarData } = useRaceSearch({
    terrain: race?.terrain_type ?? undefined,
    difficulty: race?.difficulty_level ?? undefined,
    limit: 3,
  })
  const similarRaces = (similarData?.data ?? []).filter((r) => r.id !== raceId)

  if (isLoading) return <div className="container py-12"><RaceDetailSkeleton /></div>
  if (!race) return <div className="container py-12 text-center text-muted-foreground">Race not found.</div>

  const registrationOpen = race.status === "registration_open"

  return (
    <div className="w-full py-8 md:py-12">
      <div className="container">
        <div className="mx-auto max-w-4xl space-y-10">
          {/* Hero */}
          <div className="space-y-4">
            <div className="flex flex-wrap gap-2">
              {race.terrain_type && (
                <Badge variant="secondary">{TERRAIN_LABELS[race.terrain_type] ?? race.terrain_type}</Badge>
              )}
              {race.difficulty_level && (
                <span className={cn("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium", DIFFICULTY_COLORS[race.difficulty_level] ?? "bg-gray-100 text-gray-800")}>
                  {race.difficulty_level.charAt(0).toUpperCase() + race.difficulty_level.slice(1)}
                </span>
              )}
              {race.is_certified && (
                <Badge className="gap-1"><Award className="size-3" /> Certified</Badge>
              )}
            </div>

            <h1 className="text-3xl font-bold tracking-tight md:text-4xl">{race.name}</h1>

            {race.description && (
              <p className="text-lg text-muted-foreground leading-relaxed">{race.description}</p>
            )}
          </div>

          {/* Key info */}
          <div className="rounded-lg border bg-muted/20 p-4 divide-y">
            <InfoRow
              icon={<Calendar className="size-4" />}
              label="Race date"
              value={formatDate(race.event_start_date)}
            />
            {race.event_end_date && (
              <InfoRow
                icon={<Calendar className="size-4" />}
                label="End date"
                value={formatDate(race.event_end_date)}
              />
            )}
            <InfoRow
              icon={<MapPin className="size-4" />}
              label="Location"
              value={[race.city, race.state, race.country].filter(Boolean).join(", ") || race.location}
            />
            {race.elevation_gain_m && (
              <InfoRow
                icon={<Mountain className="size-4" />}
                label="Elevation gain"
                value={`${race.elevation_gain_m.toLocaleString()} m`}
              />
            )}
            {race.website_url && (
              <div className="flex items-center gap-3 py-2">
                <Globe className="size-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground w-28 shrink-0">Website</span>
                <a
                  href={race.website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm font-medium text-primary hover:underline"
                >
                  Official site
                </a>
              </div>
            )}
          </div>

          {/* Categories */}
          {race.categories && race.categories.length > 0 && (
            <section className="space-y-4">
              <h2 className="text-xl font-semibold">Race Categories</h2>
              <div className="overflow-x-auto rounded-lg border">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-muted/50">
                      <th className="px-4 py-2 text-left font-medium">Category</th>
                      <th className="px-4 py-2 text-left font-medium">Distance</th>
                      <th className="px-4 py-2 text-left font-medium">Price</th>
                      <th className="px-4 py-2 text-left font-medium">Cutoff time</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {race.categories.map((cat) => (
                      <tr key={cat.id} className="hover:bg-muted/30">
                        <td className="px-4 py-2 font-medium">{cat.name}</td>
                        <td className="px-4 py-2">{cat.distance_km ? `${cat.distance_km} km` : "—"}</td>
                        <td className="px-4 py-2">
                          {cat.price != null ? `${cat.price} ${race.currency ?? "VND"}` : "—"}
                        </td>
                        <td className="px-4 py-2">{cat.cutoff_time_minutes ? `${cat.cutoff_time_minutes} min` : "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          {/* Course map */}
          {race.latitude != null && race.longitude != null && (
            <section className="space-y-3">
              <h2 className="text-xl font-semibold">Course Location</h2>
              <CourseMap
                latitude={race.latitude}
                longitude={race.longitude}
                name={race.name}
              />
            </section>
          )}

          {/* Tags */}
          {race.tags && race.tags.length > 0 && (
            <section className="space-y-3">
              <h2 className="text-xl font-semibold">Tags</h2>
              <div className="flex flex-wrap gap-2">
                {race.tags.map((tag) => (
                  <Badge key={tag.id} variant="outline">{tag.name}</Badge>
                ))}
              </div>
            </section>
          )}

          {/* Registration CTA */}
          <section className="rounded-lg border bg-muted/20 p-6 flex items-center justify-between gap-4 flex-wrap">
            <div>
              <div className="font-semibold text-lg">
                {registrationOpen ? "Registration is open!" : "Registration not available"}
              </div>
              {race.registration_end && (
                <div className="text-sm text-muted-foreground">
                  Closes {formatDate(race.registration_end)}
                </div>
              )}
              {race.base_price != null && (
                <div className="text-sm text-muted-foreground">
                  From {race.base_price.toLocaleString()} {race.currency ?? "VND"}
                </div>
              )}
            </div>
            {race.website_url && registrationOpen && (
              <a
                href={race.website_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 rounded-md bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90"
              >
                Register now
              </a>
            )}
          </section>

          {/* Similar races */}
          {similarRaces.length > 0 && (
            <section className="space-y-4">
              <h2 className="text-xl font-semibold">Similar Races</h2>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {similarRaces.map((r) => (
                  <RaceCard key={r.id} race={r} />
                ))}
              </div>
            </section>
          )}

          <div className="pt-4">
            <Link to="/races" className="text-sm text-primary hover:underline">
              ← Back to all races
            </Link>
          </div>
        </div>
      </div>

      {/* Floating AI assistant */}
      <RaceAssistant raceId={raceId} />
    </div>
  )
}
