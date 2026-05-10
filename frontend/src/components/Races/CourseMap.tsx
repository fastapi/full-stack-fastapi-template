import { MapPin } from "lucide-react"

interface CourseMapProps {
  latitude: number
  longitude: number
  name?: string
  className?: string
}

export function CourseMap({ latitude, longitude, name, className }: CourseMapProps) {
  // Use OpenStreetMap tile embed via iframe — no additional library needed.
  // Zoomed to show the race location pin area.
  const zoom = 13
  const bbox = 0.05

  const embedUrl =
    `https://www.openstreetmap.org/export/embed.html` +
    `?bbox=${longitude - bbox}%2C${latitude - bbox}%2C${longitude + bbox}%2C${latitude + bbox}` +
    `&layer=mapnik` +
    `&marker=${latitude}%2C${longitude}`

  return (
    <div className={className}>
      <div className="relative overflow-hidden rounded-lg border">
        <iframe
          title={name ? `Map of ${name}` : "Race location map"}
          src={embedUrl}
          width="100%"
          height="300"
          style={{ border: 0 }}
          loading="lazy"
          referrerPolicy="no-referrer"
        />
      </div>
      <p className="mt-1 flex items-center gap-1 text-xs text-muted-foreground">
        <MapPin className="size-3" />
        {latitude.toFixed(5)}, {longitude.toFixed(5)}
        {name && ` — ${name}`}
      </p>
    </div>
  )
}
