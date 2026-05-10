import type { RacePublic } from "@/client"

interface RacesMapViewProps {
  races: RacePublic[]
}

export function RacesMapView({ races }: RacesMapViewProps) {
  const racesWithCoords = races.filter(
    (r) => r.latitude != null && r.longitude != null
  )

  if (racesWithCoords.length === 0) {
    return (
      <div className="py-12 text-center text-muted-foreground">
        No races with location data to display on map.
      </div>
    )
  }

  // Calculate bounding box from all race coordinates
  const lats = racesWithCoords.map((r) => r.latitude!)
  const lons = racesWithCoords.map((r) => r.longitude!)
  const minLat = Math.min(...lats)
  const maxLat = Math.max(...lats)
  const minLon = Math.min(...lons)
  const maxLon = Math.max(...lons)

  // Add padding to bbox
  const padLat = Math.max((maxLat - minLat) * 0.15, 0.05)
  const padLon = Math.max((maxLon - minLon) * 0.15, 0.05)

  const bbox = `${minLon - padLon},${minLat - padLat},${maxLon + padLon},${maxLat + padLat}`

  // Build marker query string — OSM embed supports a single marker, so we show
  // the centroid and link to a full map with all points listed below.
  const centerLat = (minLat + maxLat) / 2
  const centerLon = (minLon + maxLon) / 2

  const embedUrl =
    `https://www.openstreetmap.org/export/embed.html` +
    `?bbox=${bbox}` +
    `&layer=mapnik` +
    `&marker=${centerLat}%2C${centerLon}`

  return (
    <div className="space-y-4">
      <div className="overflow-hidden rounded-lg border">
        <iframe
          title="Race locations map"
          src={embedUrl}
          width="100%"
          height="500"
          style={{ border: 0 }}
          loading="lazy"
          referrerPolicy="no-referrer"
        />
      </div>

      {/* Scrollable race list below map */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {racesWithCoords.map((race) => (
          <a
            key={race.id}
            href={`/races/${race.id}`}
            className="flex items-start gap-3 rounded-lg border p-3 hover:bg-muted/50 transition-colors"
          >
            <div className="mt-0.5 size-2 shrink-0 rounded-full bg-primary" />
            <div>
              <div className="text-sm font-medium leading-tight">{race.name}</div>
              <div className="text-xs text-muted-foreground">{race.location}</div>
            </div>
          </a>
        ))}
      </div>
    </div>
  )
}
