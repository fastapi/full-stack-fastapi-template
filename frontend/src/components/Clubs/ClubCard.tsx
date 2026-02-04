import { Link as RouterLink } from "@tanstack/react-router"
import { Globe, Lock, Users } from "lucide-react"

import type { ClubPublic } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface ClubCardProps {
  club: ClubPublic
  memberCount?: number
}

const visibilityConfig: Record<
  string,
  { label: string; icon: typeof Globe }
> = {
  public: { label: "Public", icon: Globe },
  private: { label: "Private", icon: Lock },
  invite_only: { label: "Invite Only", icon: Lock },
}

export function ClubCard({ club, memberCount }: ClubCardProps) {
  const visibility = visibilityConfig[club.visibility ?? "public"] ?? visibilityConfig.public
  const VisibilityIcon = visibility.icon

  return (
    <RouterLink to="/clubs/$clubId" params={{ clubId: club.id }}>
      <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer">
        {club.cover_image_url && (
          <div className="h-32 overflow-hidden rounded-t-lg">
            <img
              src={club.cover_image_url}
              alt={club.name}
              className="w-full h-full object-cover"
            />
          </div>
        )}
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between gap-2">
            <CardTitle className="text-lg line-clamp-1">{club.name}</CardTitle>
            <Badge variant="outline" className="shrink-0 gap-1">
              <VisibilityIcon className="h-3 w-3" />
              {visibility.label}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          {club.description && (
            <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
              {club.description}
            </p>
          )}
          {memberCount !== undefined && (
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              <Users className="h-4 w-4" />
              <span>
                {memberCount} {memberCount === 1 ? "member" : "members"}
              </span>
            </div>
          )}
        </CardContent>
      </Card>
    </RouterLink>
  )
}
