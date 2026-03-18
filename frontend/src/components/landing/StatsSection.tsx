import { Search, TrendingUp, Users, Zap } from "lucide-react"
import { useEffect, useState } from "react"

interface StatItem {
  icon: React.ElementType
  value: number
  suffix: string
  label: string
}

const stats: StatItem[] = [
  { icon: Users, value: 500, suffix: "+", label: "Brands Tracked" },
  { icon: Search, value: 2, suffix: "M+", label: "AI Searches Analyzed" },
  { icon: TrendingUp, value: 99.9, suffix: "%", label: "Uptime" },
  { icon: Zap, value: 150, suffix: "+", label: "Data Points Daily" },
]

function AnimatedCounter({
  value,
  suffix,
  decimals = 0,
}: {
  value: number
  suffix: string
  decimals?: number
}) {
  const [displayValue, setDisplayValue] = useState(0)

  useEffect(() => {
    const duration = 2000
    const steps = 60
    const increment = value / steps
    let current = 0

    const timer = setInterval(() => {
      current += increment
      if (current >= value) {
        setDisplayValue(value)
        clearInterval(timer)
      } else {
        setDisplayValue(current)
      }
    }, duration / steps)

    return () => clearInterval(timer)
  }, [value])

  const formatValue =
    decimals > 0
      ? displayValue.toFixed(decimals)
      : Math.floor(displayValue).toString()

  return (
    <span>
      {formatValue}
      {suffix}
    </span>
  )
}

export default function StatsSection() {
  return (
    <section className="relative py-16 bg-slate-950 overflow-hidden">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-sky-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((stat, idx) => (
            <div
              key={idx}
              className="flex flex-col items-center text-center group"
            >
              <div className="relative mb-4">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-sky-400 rounded-2xl blur-lg opacity-20 group-hover:opacity-40 transition-opacity duration-500" />
                <div className="relative w-16 h-16 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-center">
                  <stat.icon className="h-7 w-7 text-blue-400" />
                </div>
              </div>
              <div className="text-3xl md:text-4xl font-bold text-white tracking-tight">
                <AnimatedCounter
                  value={stat.value}
                  suffix={stat.suffix}
                  decimals={stat.value % 1 !== 0 ? 1 : 0}
                />
              </div>
              <div className="text-sm text-slate-400 mt-1 font-medium">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
