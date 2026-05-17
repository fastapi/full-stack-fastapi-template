import { Link, useParams } from "@tanstack/react-router"
import { Bookmark, Plus } from "lucide-react"
import type { RacePublic } from "@/client"

interface RaceCardProps {
  race: RacePublic & { ai_explanation?: string | null }
}

const terrainLabels: Record<string, string> = {
  road: "Road",
  trail: "Trail",
  track: "Track",
  mixed: "Mixed",
}

const difficultyLabels: Record<string, string> = {
  easy: "Easy",
  moderate: "Moderate",
  hard: "Hard",
  extreme: "Extreme",
}

export function RaceCard({ race }: RaceCardProps) {
  const params = useParams({ strict: false }) as Record<string, any>
  const lang = params?.lang || "vi"
  
  const aiExplanation = "ai_explanation" in race ? race.ai_explanation : null
  
  // Format date to short format like "SEP 21"
  const eventDate = race.event_start_date
    ? new Date(race.event_start_date).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      }).toUpperCase()
    : null

  const location = [race.city, race.state].filter(Boolean).join(", ").toUpperCase()
  
  // Get race distance from metadata or default
  const raceDistance = typeof race.race_metadata?.distance === 'string' 
    ? race.race_metadata.distance 
    : "13.1mi"
  
  // Build feature highlights
  const features = []
  if (race.terrain_type) features.push(terrainLabels[race.terrain_type]?.toLowerCase())
  if (race.difficulty_level) features.push(difficultyLabels[race.difficulty_level]?.toLowerCase())
  if (aiExplanation) features.push("your top match")
  const featureText = features.slice(0, 3).join(" + ") || "Scenic + rolling"

  // Participant count badge (mock for now, could come from race_metadata)
  const participantCount = typeof race.race_metadata?.participant_count === 'number'
    ? race.race_metadata.participant_count
    : 97

  return (
    <Link to="/$lang/races/$raceId" params={{ lang, raceId: race.id }} className="block group">
      <div className="overflow-hidden rounded-[22px] bg-white border border-[#E6E1D7] transition-all duration-200 hover:shadow-lg hover:border-[#0F0E0C]/20">
        {/* Image/Header Area */}
        <div className="relative h-[200px] bg-gradient-to-br from-[#5D3A2E] to-[#3D2520] overflow-hidden">
          {/* Bookmark Icon - Top Left */}
          <button
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              // TODO: Implement bookmark functionality
            }}
            className="absolute top-4 left-4 w-10 h-10 rounded-full bg-white flex items-center justify-center hover:bg-white/90 transition-colors z-10"
          >
            <Bookmark className="size-5 text-[#0F0E0C]" />
          </button>

          {/* Participant Badge - Top Right */}
          <div className="absolute top-4 right-4 bg-[#FF5A1F] text-white rounded-full px-3 py-1.5 text-sm font-bold flex items-center gap-1">
            <Plus className="size-3.5" />
            <span>{participantCount}</span>
          </div>

          {/* Location Label - Bottom Left */}
          <div className="absolute bottom-4 left-4 text-white text-xs tracking-[0.14em] font-mono uppercase">
            {location || race.location.toUpperCase()}
          </div>
        </div>

        {/* Content Area */}
        <div className="p-5 space-y-3">
          {/* Location and Date Row */}
          <div className="flex items-center justify-between text-xs text-[#74716A] uppercase tracking-wide">
            <span>{[race.city, race.state].filter(Boolean).join(", ") || race.location}</span>
            <span className="font-bold">{eventDate}</span>
          </div>

          {/* Race Name and Distance Row */}
          <div className="flex items-baseline justify-between gap-4">
            <h3 className="text-2xl font-black leading-tight flex-1 group-hover:text-[#FF5A1F] transition-colors">
              {race.name}
            </h3>
            <span className="text-2xl font-black whitespace-nowrap">
              {raceDistance}
            </span>
          </div>

          {/* Features Tag */}
          <div className="flex items-start gap-1.5 text-[#FF5A1F] text-sm">
            <Plus className="size-4 mt-0.5 flex-shrink-0" />
            <span className="leading-snug">{featureText}</span>
          </div>
        </div>
      </div>
    </Link>
  )
}
