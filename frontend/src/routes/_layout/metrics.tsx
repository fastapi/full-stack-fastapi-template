import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { BarChart3 } from "lucide-react"

import AccessDenied from "@/components/Common/AccessDenied"
import usePermissions from "@/hooks/usePermissions"

export const Route = createFileRoute("/_layout/metrics")({
  component: Metrics,
  head: () => ({
    meta: [{ title: "Metrics - FastAPI Template" }],
  }),
})

function Metrics() {
  const { can } = usePermissions()

  const { data, isLoading, isError } = useQuery({
    queryKey: ["metrics"],
    queryFn: async () => {
      const response = await fetch("/api/v1/metrics/", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token") ?? ""}`,
        },
      })
      if (!response.ok) {
        throw new Error("Failed to load metrics")
      }
      return response.json() as Promise<{ message: string }>
    },
    enabled: can("metrics:view"),
  })

  if (!can("metrics:view")) {
    return <AccessDenied />
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <BarChart3 className="h-8 w-8" />
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Metrics</h1>
          <p className="text-muted-foreground">Application insights and KPIs</p>
        </div>
      </div>
      <div className="rounded-lg border p-6">
        {isLoading ? (
          <p className="text-muted-foreground">Loading metrics...</p>
        ) : isError ? (
          <p className="text-destructive">Unable to load metrics.</p>
        ) : (
          <p>{data?.message ?? "No metrics available."}</p>
        )}
      </div>
    </div>
  )
}
