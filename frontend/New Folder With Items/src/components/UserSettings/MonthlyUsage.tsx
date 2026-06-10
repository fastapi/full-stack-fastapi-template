import { useQuery } from "@tanstack/react-query"
import { Gift } from "lucide-react"

import { StoragesService } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

const FREE_TIER_PAGE_LIMIT = 25

function getNextMonthReset(): string {
  const now = new Date()
  const next = new Date(now.getFullYear(), now.getMonth() + 1, 1)
  return next.toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  })
}

const MonthlyUsage = () => {
  const { data: storageStat } = useQuery({
    queryKey: ["storageStat"],
    queryFn: () => StoragesService.getMyStorageStat(),
  })

  const usedPages = storageStat?.total_pages ?? 0
  const percentUsed = Math.min((usedPages / FREE_TIER_PAGE_LIMIT) * 100, 100)
  const resetDate = getNextMonthReset()

  return (
    <Card>
      <CardHeader className="pb-4">
        <div>
          <CardTitle className="text-lg">Monthly Usage</CardTitle>
          <p className="text-sm text-muted-foreground">
            Track your document processing usage
          </p>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="rounded-lg border p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Gift className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium">Page Usage</span>
              <Badge variant="secondary" className="text-xs">
                Free Trial
              </Badge>
            </div>
            <div className="text-right">
              <span className="text-sm font-semibold text-primary">
                {usedPages} / {FREE_TIER_PAGE_LIMIT}
              </span>
              <p className="text-xs text-muted-foreground">
                {percentUsed.toFixed(1)}% used
              </p>
            </div>
          </div>
          <Progress value={percentUsed} className="h-2" />
        </div>
        <p className="text-sm text-muted-foreground">Resets on {resetDate}</p>
      </CardContent>
    </Card>
  )
}

export default MonthlyUsage
