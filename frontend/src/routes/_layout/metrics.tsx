import { useQuery } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"
import { Activity, UserCheck, Users } from "lucide-react"
import { MetricsService, UsersService } from "@/client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

import { ADMIN_AREA_ROLES } from "@/lib/auth/permissions"

export const Route = createFileRoute("/_layout/metrics")({
  component: MetricsPage,
  beforeLoad: async () => {
    const user = await UsersService.readUserMe()
    if (!user.role || !ADMIN_AREA_ROLES.includes(user.role)) {
      throw redirect({ to: "/forbidden" })
    }
  },
  head: () => ({
    meta: [{ title: "Metrics - FastAPI Template" }],
  }),
})

function MetricsPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["metrics"],
    queryFn: MetricsService.readMetrics,
  })

  return (
    <div className="flex flex-col gap-6 p-6">
      <div>
        <h1 className="text-3xl font-semibold">Metrics</h1>
        <p className="text-muted-foreground mt-1">
          {`Im little metrics page! Uwu (˶◕‿◕˶)`}
        </p>
      </div>

      {isLoading && <p className="text-muted-foreground">Loading metrics...</p>}

      {isError && (
        <p className="text-destructive">
          Failed to load metrics. Please try again later.
        </p>
      )}

      {data && (
        <div className="grid gap-4 md:grid-cols-3">
          <MetricCard
            label="Total Users"
            value={data.total_users}
            icon={<Users className="w-5 h-5 text-muted-foreground" />}
          />
          <MetricCard
            label="Active Users"
            value={data.active_users}
            icon={<UserCheck className="w-5 h-5 text-muted-foreground" />}
          />
          <MetricCard
            label="Total Items"
            value={data.total_items}
            icon={<Activity className="w-5 h-5 text-muted-foreground" />}
          />
        </div>
      )}
    </div>
  )
}

function MetricCard({
  label,
  value,
  icon,
}: {
  label: string
  value: number
  icon: React.ReactNode
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {label}
        </CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <p className="text-3xl font-semibold">{value}</p>
      </CardContent>
    </Card>
  )
}
