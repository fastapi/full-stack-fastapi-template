// Friendly access-denied state for unauthorized routes and actions.
import { Link } from "@tanstack/react-router"
import { ShieldX } from "lucide-react"

import { Button } from "@/components/ui/button"

type AccessDeniedProps = {
  title?: string
  message?: string
}

export default function AccessDenied({
  title = "Access Denied",
  message = "You do not have permission to view this page.",
}: AccessDeniedProps) {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4 text-center">
      <ShieldX className="h-16 w-16 text-muted-foreground" />
      <div className="space-y-2">
        <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
        <p className="max-w-md text-muted-foreground">{message}</p>
      </div>
      <Button asChild variant="outline">
        <Link to="/">Back to Dashboard</Link>
      </Button>
    </div>
  )
}
