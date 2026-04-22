import { Filter } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type { DifficultyEnum, TerrainEnum } from "@/client"

export interface RaceFilters {
  terrain: TerrainEnum | ""
  difficulty: DifficultyEnum | ""
  distanceMin: string
  distanceMax: string
}

interface FilterBarProps {
  filters: RaceFilters
  onChange: (filters: RaceFilters) => void
}

const TERRAIN_OPTIONS: { value: TerrainEnum; label: string }[] = [
  { value: "road", label: "Road" },
  { value: "trail", label: "Trail" },
  { value: "track", label: "Track" },
  { value: "mixed", label: "Mixed" },
]

const DIFFICULTY_OPTIONS: { value: DifficultyEnum; label: string }[] = [
  { value: "easy", label: "Easy" },
  { value: "moderate", label: "Moderate" },
  { value: "hard", label: "Hard" },
  { value: "extreme", label: "Extreme" },
]

const DISTANCE_PRESETS = [
  { label: "5K", min: "0", max: "6" },
  { label: "10K", min: "6", max: "15" },
  { label: "Half", min: "15", max: "25" },
  { label: "Marathon", min: "40", max: "45" },
  { label: "Ultra", min: "50", max: "" },
]

export function FilterBar({ filters, onChange }: FilterBarProps) {
  const hasFilters =
    filters.terrain !== "" ||
    filters.difficulty !== "" ||
    filters.distanceMin !== "" ||
    filters.distanceMax !== ""

  const update = (patch: Partial<RaceFilters>) => onChange({ ...filters, ...patch })

  const reset = () =>
    onChange({ terrain: "", difficulty: "", distanceMin: "", distanceMax: "" })

  return (
    <div className="flex flex-wrap items-center gap-3">
      <Filter className="size-4 text-muted-foreground shrink-0" />

      <Select
        value={filters.terrain || "all"}
        onValueChange={(v) => update({ terrain: v === "all" ? "" : (v as TerrainEnum) })}
      >
        <SelectTrigger className="w-36">
          <SelectValue placeholder="Terrain" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All terrain</SelectItem>
          {TERRAIN_OPTIONS.map((o) => (
            <SelectItem key={o.value} value={o.value}>
              {o.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select
        value={filters.difficulty || "all"}
        onValueChange={(v) =>
          update({ difficulty: v === "all" ? "" : (v as DifficultyEnum) })
        }
      >
        <SelectTrigger className="w-36">
          <SelectValue placeholder="Difficulty" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All levels</SelectItem>
          {DIFFICULTY_OPTIONS.map((o) => (
            <SelectItem key={o.value} value={o.value}>
              {o.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <div className="flex items-center gap-1">
        {DISTANCE_PRESETS.map((p) => {
          const active =
            filters.distanceMin === p.min && filters.distanceMax === p.max
          return (
            <Button
              key={p.label}
              size="sm"
              variant={active ? "default" : "outline"}
              onClick={() =>
                active
                  ? update({ distanceMin: "", distanceMax: "" })
                  : update({ distanceMin: p.min, distanceMax: p.max })
              }
            >
              {p.label}
            </Button>
          )
        })}
      </div>

      {hasFilters && (
        <Button variant="ghost" size="sm" onClick={reset}>
          Clear filters
        </Button>
      )}
    </div>
  )
}
