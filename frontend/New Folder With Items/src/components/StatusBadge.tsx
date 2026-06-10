import { AlertCircle, CheckCircle2, Circle, Clock } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface StatusBadgeProps {
  status: "pending" | "running" | "done" | "failed" | undefined
  className?: string
}

const statusConfig = {
  pending: {
    icon: Clock,
    label: "Pending",
    variant: "outline" as const,
    className: "text-yellow-600",
  },
  running: {
    icon: Circle,
    label: "Processing",
    variant: "default" as const,
    className: "text-blue-600",
  },
  done: {
    icon: CheckCircle2,
    label: "Completed",
    variant: "secondary" as const,
    className: "text-green-600",
  },
  failed: {
    icon: AlertCircle,
    label: "Error",
    variant: "destructive" as const,
    className: "text-red-600",
  },
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  if (!status) {
    return null
  }

  const config = statusConfig[status]
  const Icon = config.icon

  return (
    <Badge
      variant={config.variant}
      className={`inline-flex items-center gap-2 ${className} ${config.className}`}
    >
      <Icon
        className={`w-4 h-4 ${status === "running" ? "animate-spin" : ""}`}
      />
      <span>{config.label}</span>
    </Badge>
  )
}
