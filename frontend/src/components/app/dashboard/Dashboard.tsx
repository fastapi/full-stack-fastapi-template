import {
  Activity,
  DollarSign,
  Minus,
  TrendingDown,
  TrendingUp,
  Users,
} from "lucide-react"
import { useState } from "react"
import { BrandAwarenessScore } from "@/components/app/dashboard/components/BrandAwarenessScore"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export default function Dashboard() {
  const _stats = [
    {
      title: "Total Revenue",
      value: "$45,231.89",
      change: "+20.1%",
      changeType: "positive",
      icon: DollarSign,
      description: "from last month",
    },
    {
      title: "Active Users",
      value: "2,350",
      change: "+180",
      changeType: "positive",
      icon: Users,
      description: "new this week",
    },
    {
      title: "Conversions",
      value: "12.5%",
      change: "-2.3%",
      changeType: "negative",
      icon: TrendingUp,
      description: "vs last period",
    },
    {
      title: "Engagement",
      value: "3.2m",
      change: "+12.5%",
      changeType: "positive",
      icon: Activity,
      description: "total interactions",
    },
  ]

  const [currentScore, _setCurrentScore] = useState(7.8)
  const [previousScore, _setPreviousScore] = useState(7.2)

  // Calculate trend
  const getTrend = () => {
    const diff = currentScore - previousScore
    if (Math.abs(diff) < 0.05) return "flat"
    return diff > 0 ? "up" : "down"
  }

  const _getTrendIcon = () => {
    const trend = getTrend()
    const iconClass = "h-6 w-6"

    switch (trend) {
      case "up":
        return <TrendingUp className={`${iconClass} text-green-600`} />
      case "down":
        return <TrendingDown className={`${iconClass} text-red-600`} />
      default:
        return <Minus className={`${iconClass} text-gray-600`} />
    }
  }

  const _getTrendColor = () => {
    const trend = getTrend()
    switch (trend) {
      case "up":
        return "text-green-600"
      case "down":
        return "text-red-600"
      default:
        return "text-gray-600"
    }
  }

  // Gauge component
  const _GaugeChart = ({
    value,
    max = 10,
  }: {
    value: number
    max?: number
  }) => {
    const percentage = (value / max) * 100
    const rotation = (percentage / 100) * 180 - 90

    // Calculate color based on value (green gradient)
    const getColor = (val: number) => {
      const ratio = val / max
      if (ratio < 0.3) return "#ef4444" // red
      if (ratio < 0.5) return "#f59e0b" // orange
      if (ratio < 0.7) return "#eab308" // yellow
      if (ratio < 0.85) return "#84cc16" // light green
      return "#22c55e" // green
    }

    return (
      <div className="relative w-64 h-32 mx-auto">
        <svg viewBox="0 0 200 100" className="w-full h-full">
          {/* Background arc */}
          <path
            d="M 20 90 A 80 80 0 0 1 180 90"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="20"
            strokeLinecap="round"
          />

          {/* Gradient definition */}
          <defs>
            <linearGradient
              id="gaugeGradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="0%"
            >
              <stop offset="0%" stopColor="#ef4444" />
              <stop offset="25%" stopColor="#f59e0b" />
              <stop offset="50%" stopColor="#eab308" />
              <stop offset="75%" stopColor="#84cc16" />
              <stop offset="100%" stopColor="#22c55e" />
            </linearGradient>
          </defs>

          {/* Colored arc */}
          <path
            d="M 20 90 A 80 80 0 0 1 180 90"
            fill="none"
            stroke="url(#gaugeGradient)"
            strokeWidth="20"
            strokeLinecap="round"
            strokeDasharray={`${percentage * 2.51}, 1000`}
          />

          {/* Indicator needle */}
          <line
            x1="100"
            y1="90"
            x2="100"
            y2="30"
            stroke={getColor(value)}
            strokeWidth="3"
            strokeLinecap="round"
            transform={`rotate(${rotation} 100 90)`}
          />

          {/* Center circle */}
          <circle cx="100" cy="90" r="8" fill={getColor(value)} />

          {/* Scale markers */}
          {[0, 2, 4, 6, 8, 10].map((num) => {
            const angle = (num / max) * 180 - 90
            const rad = (angle * Math.PI) / 180
            const x = 100 + 75 * Math.cos(rad)
            const y = 90 + 75 * Math.sin(rad)
            return (
              <text
                key={num}
                x={x}
                y={y + 5}
                textAnchor="middle"
                className="text-xs fill-gray-600"
              >
                {num}
              </text>
            )
          })}
        </svg>

        {/* Score display */}
        <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 text-center">
          <div
            className="text-3xl font-bold"
            style={{ color: getColor(value) }}
          >
            {value.toFixed(1)}
          </div>
          <div className="text-xs text-gray-500">Score</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-slate-900">
              Brand Performance Dashboard
            </h1>
            <p className="text-slate-600 mt-2">
              Welcome back! Here's what's happening today.
            </p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline">Download Report</Button>
            <Button>
              <Activity className="mr-2 h-4 w-4" />
              View Analytics
            </Button>
          </div>
        </div>

        {/* Main Brand Awareness Score Section */}
        <div className="w-full mx-auto">
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">
                Brand AI Awareness Score
              </CardTitle>
              <CardDescription>
                Track and analyze your brand's AI awareness performance
              </CardDescription>
              <div className="h-px w-full bg-slate-200 shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1)]" />
            </CardHeader>

            <CardContent className="space-y-8">
              <BrandAwarenessScore />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
