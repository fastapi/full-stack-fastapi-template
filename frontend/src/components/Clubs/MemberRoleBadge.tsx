import { Crown, Shield, User } from "lucide-react"

import { Badge } from "@/components/ui/badge"

interface MemberRoleBadgeProps {
  role: string
}

const roleConfig: Record<
  string,
  { label: string; icon: typeof Crown; variant: "default" | "secondary" | "outline" }
> = {
  owner: { label: "Owner", icon: Crown, variant: "default" },
  admin: { label: "Admin", icon: Shield, variant: "secondary" },
  member: { label: "Member", icon: User, variant: "outline" },
  pending: { label: "Pending", icon: User, variant: "outline" },
}

export function MemberRoleBadge({ role }: MemberRoleBadgeProps) {
  const config = roleConfig[role] || roleConfig.member
  const Icon = config.icon

  return (
    <Badge variant={config.variant} className="gap-1">
      <Icon className="h-3 w-3" />
      {config.label}
    </Badge>
  )
}
