import { Link as RouterLink } from "@tanstack/react-router"
import { Plus } from "lucide-react"

import type { MovieSearchResult } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

import { MoviePoster } from "./MoviePoster"

interface MovieCardProps {
  movie: MovieSearchResult
  onAddToWatchlist?: () => void
  showAddButton?: boolean
}

export function MovieCard({
  movie,
  onAddToWatchlist,
  showAddButton = true,
}: MovieCardProps) {
  return (
    <Card className="group overflow-hidden hover:shadow-lg transition-shadow">
      <RouterLink to="/movies/$imdbId" params={{ imdbId: movie.imdb_id }}>
        <div className="relative aspect-[2/3] overflow-hidden">
          <MoviePoster
            posterUrl={movie.poster_url}
            title={movie.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          {movie.type && (
            <Badge className="absolute top-2 right-2 capitalize">
              {movie.type}
            </Badge>
          )}
        </div>
      </RouterLink>
      <CardContent className="p-4">
        <RouterLink to="/movies/$imdbId" params={{ imdbId: movie.imdb_id }}>
          <h3 className="font-display font-semibold text-lg line-clamp-2 hover:text-primary transition-colors">
            {movie.title}
          </h3>
        </RouterLink>
        <p className="text-muted-foreground text-sm mt-1">{movie.year}</p>
        {showAddButton && onAddToWatchlist && (
          <Button
            variant="outline"
            size="sm"
            className="w-full mt-3"
            onClick={(e) => {
              e.preventDefault()
              onAddToWatchlist()
            }}
          >
            <Plus className="h-4 w-4 mr-2" />
            Add to Watchlist
          </Button>
        )}
      </CardContent>
    </Card>
  )
}
