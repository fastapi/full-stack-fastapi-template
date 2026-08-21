import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"
import { Suspense } from "react"

import { MetricsService, UsersService } from "@/client"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { hasPermission, PERMISSIONS } from "@/utils"

function getMetricsQueryOptions() {
  return {
    queryFn: async () => (await MetricsService.readMetrics()).data,
    queryKey: ["metrics"],
  }
}

export const Route = createFileRoute("/_layout/metrics")({
  component: Metrics,
  beforeLoad: async () => {
    const { data: user } = await UsersService.readUserMe()
    if (!hasPermission(user, PERMISSIONS.metricsView)) {
      throw redirect({
        to: "/forbidden",
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

function MetricsCards() {
  const { data: metrics } = useSuspenseQuery(getMetricsQueryOptions())

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <Card>
        <CardHeader>
          <CardDescription>Users</CardDescription>
          <CardTitle className="text-3xl">{metrics.user_count}</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Total registered accounts
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardDescription>Items</CardDescription>
          <CardTitle className="text-3xl">{metrics.item_count}</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Total items across all users
        </CardContent>
      </Card>
    </div>
  )
}

function PendingMetrics() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <Skeleton className="h-32" />
      <Skeleton className="h-32" />
    </div>
  )
}

function Metrics() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Metrics</h1>
        <p className="text-muted-foreground">Basic usage insights</p>
      </div>
      <Suspense fallback={<PendingMetrics />}>
        <MetricsCards />
      </Suspense>
    </div>
  )
}
