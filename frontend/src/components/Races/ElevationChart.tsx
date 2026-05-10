interface ElevationPoint {
  distance_km: number
  elevation_m: number
}

interface ElevationChartProps {
  points: ElevationPoint[]
  className?: string
}

export function ElevationChart({ points, className }: ElevationChartProps) {
  if (points.length < 2) return null

  const W = 600
  const H = 160
  const PAD = { top: 12, right: 8, bottom: 28, left: 44 }

  const minElev = Math.min(...points.map((p) => p.elevation_m))
  const maxElev = Math.max(...points.map((p) => p.elevation_m))
  const elevRange = maxElev - minElev || 1
  const maxDist = points[points.length - 1].distance_km

  const toX = (d: number) => PAD.left + (d / maxDist) * (W - PAD.left - PAD.right)
  const toY = (e: number) =>
    PAD.top + (1 - (e - minElev) / elevRange) * (H - PAD.top - PAD.bottom)

  const linePath = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${toX(p.distance_km).toFixed(1)} ${toY(p.elevation_m).toFixed(1)}`)
    .join(" ")

  const fillPath =
    linePath +
    ` L ${toX(maxDist).toFixed(1)} ${(H - PAD.bottom).toFixed(1)}` +
    ` L ${toX(0).toFixed(1)} ${(H - PAD.bottom).toFixed(1)} Z`

  const yTicks = [minElev, minElev + elevRange / 2, maxElev]

  return (
    <div className={className}>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full text-xs"
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Fill area */}
        <path d={fillPath} fill="hsl(var(--primary) / 0.15)" />
        {/* Line */}
        <path d={linePath} fill="none" stroke="hsl(var(--primary))" strokeWidth="2" />

        {/* Y-axis ticks */}
        {yTicks.map((e) => (
          <g key={e}>
            <line
              x1={PAD.left}
              y1={toY(e)}
              x2={W - PAD.right}
              y2={toY(e)}
              stroke="currentColor"
              strokeOpacity="0.1"
            />
            <text
              x={PAD.left - 4}
              y={toY(e) + 4}
              textAnchor="end"
              fill="currentColor"
              opacity="0.5"
            >
              {Math.round(e)}m
            </text>
          </g>
        ))}

        {/* X-axis labels */}
        {[0, maxDist / 2, maxDist].map((d) => (
          <text
            key={d}
            x={toX(d)}
            y={H - 4}
            textAnchor="middle"
            fill="currentColor"
            opacity="0.5"
          >
            {d.toFixed(0)}km
          </text>
        ))}
      </svg>
    </div>
  )
}
