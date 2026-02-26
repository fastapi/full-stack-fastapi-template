import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import useAuth from "@/hooks/useAuth"
import { listRecentTemplates } from "@/lib/templateMvpApi"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: "Dashboard - TemplateForge AI",
      },
    ],
  }),
})

function Dashboard() {
  const { user: currentUser } = useAuth()
  const recentTemplatesQuery = useQuery({
    queryKey: ["dashboard", "recent-templates", 5],
    queryFn: () => listRecentTemplates(5),
    staleTime: 60_000,
  })
  const recentTemplates = recentTemplatesQuery.data?.data ?? []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl truncate max-w-sm">
          Hi, {currentUser?.full_name || currentUser?.email}
        </h1>
        <p className="text-muted-foreground">
          Welcome back, nice to see you again!!!
        </p>
      </div>

      <section className="rounded-lg border bg-card p-4">
        <div className="mb-3">
          <h2 className="text-lg font-semibold">Recently Used Templates</h2>
          <p className="text-sm text-muted-foreground">
            Based on your saved generations
          </p>
        </div>

        {recentTemplatesQuery.isLoading ? (
          <p className="text-sm text-muted-foreground">
            Loading recent templates...
          </p>
        ) : recentTemplatesQuery.isError ? (
          <p className="text-sm text-destructive">
            Failed to load recent templates.
          </p>
        ) : recentTemplates.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No recent templates yet. Save a generation to see it here.
          </p>
        ) : (
          <div className="space-y-2">
            {recentTemplates.map((template) => (
              <div
                key={template.template_id}
                className="rounded-md border px-3 py-2"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <p className="truncate font-medium">
                      {template.template_name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {template.category} • {template.language}
                    </p>
                  </div>
                  <div className="shrink-0 text-right">
                    <p className="text-xs text-muted-foreground">
                      {formatLastUsed(template.last_used_at)}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {template.usage_count} use
                      {template.usage_count === 1 ? "" : "s"}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

function formatLastUsed(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return "Last used: unknown"
  }
  return `Last used: ${date.toLocaleString()}`
}
