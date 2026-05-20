import { createFileRoute, Link } from "@tanstack/react-router"
import { ShieldAlert } from "lucide-react"
import { Button } from "@/components/ui/button"

export const Route = createFileRoute("/_layout/forbidden")({
  component: Forbidden,
  head: () => ({
    meta: [{ title: "Access Denied - FastAPI Template" }],
  }),
})

function Forbidden() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 text-center px-4">
      <ShieldAlert className="w-16 h-16 text-muted-foreground" />
      <h1 className="text-3xl font-semibold">Access Denied</h1>
      <p className="text-muted-foreground max-w-md">
        You don't have permission to view this page. If you think this is a
        mistake, contact your administrator.
      </p>
      <Button asChild>
        <Link to="/">Back to Dashboard</Link>
      </Button>
    </div>
  )
}
