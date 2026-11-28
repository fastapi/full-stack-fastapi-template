import { useQuery } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"

import { MetricsService, UsersService } from "@/client"
import { isStaff } from "@/lib/roles"

export const Route = createFileRoute("/_layout/metrics")({
  component: Metrics,
  beforeLoad: async () => {
    const { data: user } = await UsersService.readUserMe()
    if (!isStaff(user)) {
      throw redirect({
        to: "/",
      })
    }
  },
  head: () => ({
    meta: [
      {
        title: "Metrics - FastAPI Template",
      },
    ],
  }),
})

function Metrics() {
  const { data: metrics } = useQuery({
    queryKey: ["metrics"],
    queryFn: async () => (await MetricsService.readMetrics()).data,
  })

  const stats = [
    { label: "Total users", value: metrics?.total_users },
    { label: "Active users", value: metrics?.active_users },
    { label: "Total items", value: metrics?.total_items },
  ]

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Metrics</h1>
        <p className="text-muted-foreground">Overview of users and items</p>
      </div>
      <dl className="grid gap-4 sm:grid-cols-3">
        {stats.map((stat) => (
          <div key={stat.label} className="rounded-xl border p-6">
            <dt className="text-muted-foreground text-sm">{stat.label}</dt>
            <dd className="text-2xl font-bold">{stat.value ?? "—"}</dd>
          </div>
        ))}
      </dl>
    </div>
  )
}
