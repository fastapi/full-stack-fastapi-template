import { Calendar, Mail } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import useAuth from "@/hooks/useAuth"

function getInitials(fullName: string | null | undefined, email: string) {
  if (fullName?.trim()) {
    return fullName
      .trim()
      .split(/\s+/)
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2)
  }
  return email.slice(0, 2).toUpperCase()
}

function formatJoinedDate(createdAt: string | null | undefined) {
  if (!createdAt) return null
  const date = new Date(createdAt)
  return date.toLocaleDateString("en-US", { month: "long", year: "numeric" })
}

export function ProfileHeader() {
  const { user } = useAuth()

  if (!user) return null

  const initials = getInitials(user.full_name, user.email)
  const joinedDate = formatJoinedDate(user.created_at)

  return (
    <Card>
      <CardContent>
        <div className="flex flex-col items-start gap-6 md:flex-row md:items-center">
          <div className="relative">
            <Avatar className="h-24 w-24">
              <AvatarImage src={undefined} alt="" />
              <AvatarFallback className="text-2xl" aria-hidden>
                {initials}
              </AvatarFallback>
            </Avatar>
          </div>
          <div className="flex-1 space-y-2">
            <div className="flex flex-col gap-2 md:flex-row md:items-center">
              <h1 className="text-2xl font-bold">
                {user.full_name?.trim() || user.email}
              </h1>
              {user.is_superuser && <Badge variant="secondary">Admin</Badge>}
            </div>
            <div className="text-muted-foreground flex flex-wrap gap-4 text-sm">
              <div className="flex items-center gap-1">
                <Mail className="size-4 shrink-0" aria-hidden />
                <span>{user.email}</span>
              </div>
              {joinedDate && (
                <div className="flex items-center gap-1">
                  <Calendar className="size-4 shrink-0" aria-hidden />
                  <span>Joined {joinedDate}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
