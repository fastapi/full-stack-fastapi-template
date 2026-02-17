import { Minus, TrendingDown, TrendingUp } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

interface MetricCardProps {
  title: string
  currentValue: number
  previousValue: number | null
  change: number | null
  hasPrevious: boolean
  format?: "score" | "percentage"
}

export function MetricCard({
  title,
  currentValue,
  previousValue,
  change,
  hasPrevious,
  format = "score",
}: MetricCardProps) {
  const formatValue = (val: number) => {
    if (format === "percentage") {
      return `${(val * 100).toFixed(1)}%`
    }
    return val.toFixed(1)
  }

  const getTrend = (): "up" | "down" | "flat" => {
    if (!hasPrevious || change === null) return "flat"
    if (Math.abs(change) < 0.001) return "flat"
    return change > 0 ? "up" : "down"
  }

  const trend = getTrend()

  const getTrendIcon = () => {
    const iconClass = "h-4 w-4"
    switch (trend) {
      case "up":
        return <TrendingUp className={`${iconClass} text-green-600`} />
      case "down":
        return <TrendingDown className={`${iconClass} text-red-600`} />
      default:
        return <Minus className={`${iconClass} text-gray-400`} />
    }
  }

  const getTrendColor = () => {
    switch (trend) {
      case "up":
        return "text-green-600"
      case "down":
        return "text-red-600"
      default:
        return "text-gray-500"
    }
  }

  const formatChange = () => {
    if (!hasPrevious || change === null) return "N/A"
    const absChange = Math.abs(change)
    if (format === "percentage") {
      return `${(absChange * 100).toFixed(1)}%`
    }
    return absChange.toFixed(2)
  }

  return (
    <Card className="shadow-md hover:shadow-lg transition-shadow">
      <CardContent className="pt-6">
        <div className="space-y-2">
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <div className="flex items-end justify-between">
            <p className="text-3xl font-bold text-slate-900">
              {formatValue(currentValue)}
            </p>
            <div className="flex items-center gap-1">
              {getTrendIcon()}
              <span className={`text-sm font-medium ${getTrendColor()}`}>
                {trend === "up" && "+"}
                {trend === "down" && "-"}
                {formatChange()}
              </span>
            </div>
          </div>
          {hasPrevious && previousValue !== null && (
            <p className="text-xs text-slate-400">
              Previous: {formatValue(previousValue)}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
