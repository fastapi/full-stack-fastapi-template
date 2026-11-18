import { useQuery } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"

import { MetricsService, UsersService } from "@/client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export const Route = createFileRoute("/_layout/metrics")({
  component: Metrics,
  beforeLoad: async () => {
    const { data: user } = await UsersService.readUserMe()
    if (user.role !== "admin" && user.role !== "manager") {
      throw redirect({ to: "/" })
    }
  },
  head: () => ({
    meta: [{ title: "Metrics - FastAPI Template" }],
  }),
})

function Metrics() {
  const { data: metrics, isPending } = useQuery({
    queryKey: ["metrics"],
    queryFn: async () => (await MetricsService.readMetrics()).data,
  })

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Metrics</h1>
        <p className="text-muted-foreground">Application overview</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Users</CardTitle>
          </CardHeader>
          <CardContent className="text-3xl font-semibold">
            {isPending ? "..." : metrics?.user_count}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Items</CardTitle>
          </CardHeader>
          <CardContent className="text-3xl font-semibold">
            {isPending ? "..." : metrics?.item_count}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
