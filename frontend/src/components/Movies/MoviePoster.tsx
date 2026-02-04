import { Film } from "lucide-react"

import { cn } from "@/lib/utils"

interface MoviePosterProps {
  posterUrl: string | null | undefined
  title: string
  className?: string
}

export function MoviePoster({ posterUrl, title, className }: MoviePosterProps) {
  if (!posterUrl) {
    return (
      <div
        className={cn(
          "flex items-center justify-center bg-muted rounded-md",
          className,
        )}
      >
        <div className="text-center p-4">
          <Film className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
          <span className="text-sm text-muted-foreground">No poster</span>
        </div>
      </div>
    )
  }

  return (
    <img
      src={posterUrl}
      alt={`${title} poster`}
      className={cn("rounded-md", className)}
      loading="lazy"
    />
  )
}
