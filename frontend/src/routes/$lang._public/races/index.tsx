import { createFileRoute } from "@tanstack/react-router"
import { Loader2, LayoutGrid, Map } from "lucide-react"
import { useCallback, useDeferredValue, useState } from "react"
import { FilterBar, type RaceFilters } from "@/components/Races/FilterBar"
import { RaceCard } from "@/components/Races/RaceCard"
import { RacesMapView } from "@/components/Races/RacesMapView"
import { SearchBar } from "@/components/Races/SearchBar"
import { SortControls, type SortOption } from "@/components/Races/SortControls"
import { useRaceSearch } from "@/hooks/useRaceSearch"
import type { DifficultyEnum, TerrainEnum } from "@/client"
import { cn } from "@/lib/utils"
import { generateMetaTags, generateBreadcrumbSchema, StructuredData } from "@/lib/seo"

const baseUrl = import.meta.env.VITE_FRONTEND_URL || "https://vnrunner.com"

interface RaceSearch {
  q?: string
  terrain?: string
  difficulty?: string
  distanceMin?: string
  distanceMax?: string
  provinceCode?: string
  sort?: "date" | "popularity"
  page?: number
}

function validateSearch(search: Record<string, unknown>): RaceSearch {
  return {
    q: typeof search.q === "string" ? search.q : "",
    terrain: typeof search.terrain === "string" ? search.terrain : "",
    difficulty: typeof search.difficulty === "string" ? search.difficulty : "",
    distanceMin: typeof search.distanceMin === "string" ? search.distanceMin : "",
    distanceMax: typeof search.distanceMax === "string" ? search.distanceMax : "",
    provinceCode: typeof search.provinceCode === "string" ? search.provinceCode : "",
    sort:
      search.sort === "date" || search.sort === "popularity"
        ? search.sort
        : "date",
    page: typeof search.page === "number" ? search.page : 0,
  }
}

export const Route = createFileRoute("/$lang/_public/races/")({
  validateSearch,
  component: RacesPage,
  head: () => ({
    meta: generateMetaTags({
      title: "Browse Running Races in Vietnam | VNRunner",
      description:
        "Find and register for upcoming running races in Vietnam. Filter by distance, location, terrain (road, trail), and difficulty. Discover marathons, ultras, 5K, 10K, and half marathons across Vietnam. Secure online registration.",
      keywords: "Vietnam races, running events Vietnam, trail running, road races, marathon registration, ultra marathon Vietnam, 5K Vietnam, 10K Vietnam, half marathon Vietnam",
      canonicalUrl: `${baseUrl}/races`,
    }),
  }),
})

const PAGE_SIZE = 18

function RacesPage() {
  const search = Route.useSearch()
  const navigate = Route.useNavigate()

  const deferredQ = useDeferredValue(search.q)

  const { data, isLoading, isFetching } = useRaceSearch({
    q: deferredQ || undefined,
    terrain: (search.terrain as TerrainEnum) || undefined,
    difficulty: (search.difficulty as DifficultyEnum) || undefined,
    distanceMin: search.distanceMin || undefined,
    distanceMax: search.distanceMax || undefined,
    provinceCode: search.provinceCode || undefined,
    sort: search.sort,
    skip: (search.page ?? 0) * PAGE_SIZE,
    limit: PAGE_SIZE,
  })

  const races = data?.data ?? []
  const totalCount = data?.count ?? 0
  const totalPages = Math.ceil(totalCount / PAGE_SIZE)
  const currentPage = search.page ?? 0
  const [viewMode, setViewMode] = useState<"grid" | "map">("grid")

  const breadcrumbSchema = generateBreadcrumbSchema([
    { name: "Home", url: baseUrl },
    { name: "Races", url: `${baseUrl}/races` },
  ])

  const setSearch = useCallback(
    (patch: Partial<typeof search>) => {
      navigate({ search: (prev) => ({ ...prev, ...patch, page: 0 }) })
    },
    [navigate],
  )

  const handleQueryChange = useCallback(
    (q: string) => setSearch({ q }),
    [setSearch],
  )

  const handleFilterChange = useCallback(
    (filters: RaceFilters) => {
      setSearch({
        terrain: filters.terrain,
        difficulty: filters.difficulty,
        distanceMin: filters.distanceMin,
        distanceMax: filters.distanceMax,
        provinceCode: filters.provinceCode,
      })
    },
    [setSearch],
  )

  const handleSortChange = useCallback(
    (sort: SortOption) => setSearch({ sort }),
    [setSearch],
  )

  const filters: RaceFilters = {
    terrain: (search.terrain as TerrainEnum) || "",
    difficulty: (search.difficulty as DifficultyEnum) || "",
    distanceMin: search.distanceMin || "",
    distanceMax: search.distanceMax || "",
    provinceCode: search.provinceCode || "",
  }

  return (
    <div className="w-full py-8 md:py-12">
      <StructuredData data={breadcrumbSchema} />
      <div className="container">
        <div className="mx-auto max-w-7xl space-y-8">
          {/* Header */}
          <header className="space-y-4">
            <h1 className="text-3xl font-bold tracking-tight md:text-4xl">
              Upcoming Races in Vietnam
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl">
              Browse and register for upcoming running races across Vietnam. Find the perfect event
              that matches your goals and fitness level - from road races to trail runs, 5Ks to ultramarathons.
            </p>
          </header>

          {/* Search + Controls */}
          <div className="space-y-3 rounded-lg border bg-muted/30 p-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              <SearchBar
                value={search.q ?? ""}
                onChange={handleQueryChange}
              />
              <SortControls value={search.sort ?? "date"} onChange={handleSortChange} />
            </div>
            <FilterBar filters={filters} onChange={handleFilterChange} />
          </div>

          {/* Results count + view toggle */}
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>
              {isLoading
                ? "Searching..."
                : `${totalCount} race${totalCount !== 1 ? "s" : ""} found`}
            </span>
            <div className="flex items-center gap-2">
              {isFetching && !isLoading && <Loader2 className="size-4 animate-spin" />}
              <div className="flex rounded-md border overflow-hidden">
                <button
                  onClick={() => setViewMode("grid")}
                  className={cn("px-2 py-1", viewMode === "grid" ? "bg-muted text-foreground" : "hover:bg-muted/50")}
                  title="Grid view"
                >
                  <LayoutGrid className="size-4" />
                </button>
                <button
                  onClick={() => setViewMode("map")}
                  className={cn("px-2 py-1 border-l", viewMode === "map" ? "bg-muted text-foreground" : "hover:bg-muted/50")}
                  title="Map view"
                >
                  <Map className="size-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Races Grid / Map */}
          {isLoading ? (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <div
                  key={i}
                  className="h-64 rounded-lg border bg-muted/50 animate-pulse"
                />
              ))}
            </div>
          ) : viewMode === "map" ? (
            <RacesMapView races={races} />
          ) : races.length > 0 ? (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {races.map((race) => (
                <RaceCard key={race.id} race={race} />
              ))}
            </div>
          ) : (
            <div className="py-12 text-center">
              <p className="text-lg text-muted-foreground">
                No races found matching your filters. Try adjusting your search.
              </p>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 pt-4">
              <button
                className="rounded border px-3 py-1.5 text-sm disabled:opacity-40"
                disabled={currentPage === 0}
                onClick={() => navigate({ search: (prev) => ({ ...prev, page: currentPage - 1 }) })}
              >
                Previous
              </button>
              <span className="text-sm text-muted-foreground">
                Page {currentPage + 1} of {totalPages}
              </span>
              <button
                className="rounded border px-3 py-1.5 text-sm disabled:opacity-40"
                disabled={currentPage >= totalPages - 1}
                onClick={() => navigate({ search: (prev) => ({ ...prev, page: currentPage + 1 }) })}
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default RacesPage
