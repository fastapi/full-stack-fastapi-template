import { ChartColumnBig, ChartLine } from "lucide-react"
import { useState } from "react"
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import type { CompetitorRankingDetailDataPoint } from "@/clients/dashboard"
import {
  axisProps,
  CHART_COLORS,
  gridProps,
  tooltipClasses,
} from "@/components/app/dashboard/components/chartTheme"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

// ── Types ──────────────────────────────────────────────────────────────────────

interface CompetitorRankingDetailChartProps {
  dataPoints: CompetitorRankingDetailDataPoint[]
  brandName: string
  competitorName: string
}

interface ChartPoint {
  date: string
  displayDate: string
  brand_best: number | null
  comp_best: number | null
  best_gap: number | null
  brand_worst: number | null
  comp_worst: number | null
  worst_gap: number | null
  brand_avg: number | null
  comp_avg: number | null
  avg_gap: number | null
}

type GroupKey = "best" | "worst" | "avg"

// ── Group config ───────────────────────────────────────────────────────────────

interface GroupConfig {
  key: GroupKey
  label: string
  brandKey: keyof ChartPoint
  compKey: keyof ChartPoint
  gapKey: keyof ChartPoint
  brandColor: string
  compColor: string
  gapColor: string
  tooltipFmt: (v: number) => string
  tooltipGapFmt: (v: number) => string
  yTickFormatter: (v: number) => string
}

const GROUPS: GroupConfig[] = [
  {
    key: "best",
    label: "Best Ranking",
    brandKey: "brand_best",
    compKey: "comp_best",
    gapKey: "best_gap",
    brandColor: CHART_COLORS.green,
    compColor: CHART_COLORS.greenLight,
    gapColor: "#065f46",
    tooltipFmt: (v) => `#${Math.round(v)}`,
    tooltipGapFmt: (v) => `${v > 0 ? "+" : ""}${v.toFixed(1)}`,
    yTickFormatter: (v) => `#${Math.round(v)}`,
  },
  {
    key: "worst",
    label: "Worst Ranking",
    brandKey: "brand_worst",
    compKey: "comp_worst",
    gapKey: "worst_gap",
    brandColor: CHART_COLORS.red,
    compColor: "#fb7185",
    gapColor: "#9f1239",
    tooltipFmt: (v) => `#${Math.round(v)}`,
    tooltipGapFmt: (v) => `${v > 0 ? "+" : ""}${v.toFixed(1)}`,
    yTickFormatter: (v) => `#${Math.round(v)}`,
  },
  {
    key: "avg",
    label: "Average Ranking",
    brandKey: "brand_avg",
    compKey: "comp_avg",
    gapKey: "avg_gap",
    brandColor: CHART_COLORS.amber,
    compColor: "#fbbf24",
    gapColor: "#92400e",
    tooltipFmt: (v) => `#${v.toFixed(1)}`,
    tooltipGapFmt: (v) => `${v > 0 ? "+" : ""}${v.toFixed(1)}`,
    yTickFormatter: (v) => `#${v.toFixed(0)}`,
  },
]

// ── Data transform ─────────────────────────────────────────────────────────────

const formatDate = (iso: string): string => {
  const d = new Date(iso)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

function buildChartData(
  points: CompetitorRankingDetailDataPoint[],
): ChartPoint[] {
  return points.map((p) => ({
    date: p.date,
    displayDate: formatDate(p.date),
    brand_best: p.brand_best != null ? p.brand_best : null,
    comp_best: p.comp_best != null ? p.comp_best : null,
    best_gap: p.best_gap != null ? +p.best_gap.toFixed(1) : null,
    brand_worst: p.brand_worst != null ? p.brand_worst : null,
    comp_worst: p.comp_worst != null ? p.comp_worst : null,
    worst_gap: p.worst_gap != null ? +p.worst_gap.toFixed(1) : null,
    brand_avg: p.brand_avg != null ? +p.brand_avg.toFixed(1) : null,
    comp_avg: p.comp_avg != null ? +p.comp_avg.toFixed(1) : null,
    avg_gap: p.avg_gap != null ? +p.avg_gap.toFixed(1) : null,
  }))
}

// ── Tooltip ────────────────────────────────────────────────────────────────────

interface SubChartTooltipProps {
  active?: boolean
  payload?: readonly any[]
  label?: string | number
  group: GroupConfig
  brandName: string
  competitorName: string
}

const SubChartTooltip = ({
  active,
  payload,
  label,
  group,
  brandName,
  competitorName,
}: SubChartTooltipProps) => {
  if (!active || !payload || payload.length === 0) return null

  const find = (key: string) => payload.find((e: any) => e.dataKey === key)
  const brandVal = find(group.brandKey as string)?.value
  const compVal = find(group.compKey as string)?.value
  const gapVal = find(group.gapKey as string)?.value

  return (
    <div className={tooltipClasses.container}>
      <p className={tooltipClasses.label}>{label}</p>
      {brandVal != null && (
        <div className={tooltipClasses.row}>
          <div className="flex items-center gap-1.5">
            <span
              className="w-2 h-2 rounded-full flex-shrink-0"
              style={{ backgroundColor: group.brandColor }}
            />
            <span className={tooltipClasses.name}>{brandName}</span>
          </div>
          <span className={tooltipClasses.value}>
            {group.tooltipFmt(brandVal)}
          </span>
        </div>
      )}
      {compVal != null && (
        <div className={tooltipClasses.row}>
          <div className="flex items-center gap-1.5">
            <span
              className="w-2 h-2 rounded-full flex-shrink-0"
              style={{ backgroundColor: group.compColor }}
            />
            <span className={tooltipClasses.name}>{competitorName}</span>
          </div>
          <span className={tooltipClasses.value}>
            {group.tooltipFmt(compVal)}
          </span>
        </div>
      )}
      {gapVal != null && (
        <div className={tooltipClasses.row}>
          <div className="flex items-center gap-1.5">
            <span
              className="w-2 h-2 rounded-full flex-shrink-0"
              style={{ backgroundColor: group.gapColor }}
            />
            <span className={tooltipClasses.name}>Gap</span>
          </div>
          <span
            className={`font-semibold ${gapVal > 0 ? "text-emerald-400" : gapVal < 0 ? "text-red-400" : "text-slate-400"}`}
          >
            {group.tooltipGapFmt(gapVal)}
          </span>
        </div>
      )}
      <p className={tooltipClasses.note}>
        positive = brand ranks higher · lower # = better
      </p>
    </div>
  )
}

// ── Sub-chart ──────────────────────────────────────────────────────────────────

interface SubChartProps {
  group: GroupConfig
  data: ChartPoint[]
  chartType: "line" | "bar"
  brandName: string
  competitorName: string
}

function SubChart({
  group,
  data,
  chartType,
  brandName,
  competitorName,
}: SubChartProps) {
  const tooltipContent = (props: any) => (
    <SubChartTooltip
      {...props}
      group={group}
      brandName={brandName}
      competitorName={competitorName}
    />
  )

  return (
    <div className="w-full h-40">
      <ResponsiveContainer width="100%" height="100%">
        {chartType === "line" ? (
          <LineChart
            data={data}
            margin={{ top: 4, right: 4, left: -16, bottom: 0 }}
          >
            <CartesianGrid {...gridProps} />
            <ReferenceLine
              y={0}
              stroke="#cbd5e1"
              strokeDasharray="4 2"
              strokeWidth={1}
            />
            <XAxis dataKey="displayDate" {...axisProps} />
            <YAxis
              {...axisProps}
              reversed
              tickFormatter={group.yTickFormatter}
            />
            <Tooltip content={tooltipContent} />
            {/* Brand — solid */}
            <Line
              type="monotone"
              dataKey={group.brandKey as string}
              stroke={group.brandColor}
              strokeWidth={2}
              dot={false}
              connectNulls={false}
              activeDot={{
                r: 3,
                strokeWidth: 2,
                stroke: "#fff",
                fill: group.brandColor,
              }}
            />
            {/* Competitor — long dash */}
            <Line
              type="monotone"
              dataKey={group.compKey as string}
              stroke={group.compColor}
              strokeWidth={2}
              strokeDasharray="5 3"
              dot={false}
              connectNulls={false}
              activeDot={{
                r: 3,
                strokeWidth: 2,
                stroke: "#fff",
                fill: group.compColor,
              }}
            />
            {/* Gap — dotted */}
            <Line
              type="monotone"
              dataKey={group.gapKey as string}
              stroke={group.gapColor}
              strokeWidth={1.5}
              strokeDasharray="2 4"
              dot={false}
              connectNulls={false}
              activeDot={{
                r: 3,
                strokeWidth: 2,
                stroke: "#fff",
                fill: group.gapColor,
              }}
            />
          </LineChart>
        ) : (
          <BarChart
            data={data}
            margin={{ top: 4, right: 4, left: -16, bottom: 0 }}
            barCategoryGap="25%"
          >
            <CartesianGrid {...gridProps} />
            <ReferenceLine
              y={0}
              stroke="#cbd5e1"
              strokeDasharray="4 2"
              strokeWidth={1}
            />
            <XAxis dataKey="displayDate" {...axisProps} />
            <YAxis
              {...axisProps}
              reversed
              tickFormatter={group.yTickFormatter}
            />
            <Tooltip content={tooltipContent} />
            <Bar
              dataKey={group.brandKey as string}
              fill={group.brandColor}
              radius={[2, 2, 0, 0]}
            />
            <Bar
              dataKey={group.compKey as string}
              fill={group.compColor}
              radius={[2, 2, 0, 0]}
            />
            <Bar
              dataKey={group.gapKey as string}
              fill={group.gapColor}
              fillOpacity={0.7}
              radius={[2, 2, 0, 0]}
            />
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  )
}

// ── Shared legend strip ────────────────────────────────────────────────────────

function SharedLegend({
  brandName,
  competitorName,
}: {
  brandName: string
  competitorName: string
}) {
  return (
    <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1 text-xs text-slate-500 mt-1">
      <div className="flex items-center gap-1.5">
        <svg width="18" height="8" className="flex-shrink-0">
          <title>Brand ranking line</title>
          <line x1="0" y1="4" x2="18" y2="4" stroke="#6b7280" strokeWidth="2" />
        </svg>
        <span>{brandName}</span>
      </div>
      <div className="flex items-center gap-1.5">
        <svg width="18" height="8" className="flex-shrink-0">
          <title>Competitor ranking line</title>
          <line
            x1="0"
            y1="4"
            x2="18"
            y2="4"
            stroke="#6b7280"
            strokeWidth="2"
            strokeDasharray="5 3"
          />
        </svg>
        <span>{competitorName}</span>
      </div>
      <div className="flex items-center gap-1.5">
        <svg width="18" height="8" className="flex-shrink-0">
          <title>Ranking gap line</title>
          <line
            x1="0"
            y1="4"
            x2="18"
            y2="4"
            stroke="#94a3b8"
            strokeWidth="1.5"
            strokeDasharray="2 4"
          />
        </svg>
        <span>Gap</span>
      </div>
      <span className="text-slate-400">· lower # = better</span>
    </div>
  )
}

// ── Main component ─────────────────────────────────────────────────────────────

export function CompetitorRankingDetailChart({
  dataPoints,
  brandName,
  competitorName,
}: CompetitorRankingDetailChartProps) {
  const [chartType, setChartType] = useState<"line" | "bar">("line")
  const [enabledGroups, setEnabledGroups] = useState<Set<GroupKey>>(
    new Set(["best", "worst", "avg"]),
  )

  const toggleGroup = (key: GroupKey) => {
    setEnabledGroups((prev) => {
      const next = new Set(prev)
      if (next.has(key)) {
        if (next.size === 1) return prev // keep at least one visible
        next.delete(key)
      } else {
        next.add(key)
      }
      return next
    })
  }

  const chartData = buildChartData(dataPoints)

  if (chartData.length === 0) {
    return (
      <div className="w-full h-64 flex items-center justify-center text-slate-400 text-sm">
        No ranking data available for the selected range
      </div>
    )
  }

  const activeGroups = GROUPS.filter((g) => enabledGroups.has(g.key))

  return (
    <div className="space-y-2">
      {/* Controls row */}
      <div className="flex items-center justify-between">
        {/* Category toggles */}
        <div className="flex flex-wrap gap-1">
          {GROUPS.map((g) => {
            const active = enabledGroups.has(g.key)
            return (
              <button
                key={g.key}
                type="button"
                onClick={() => toggleGroup(g.key)}
                className={[
                  "px-2 py-0.5 rounded text-xs font-medium transition-colors whitespace-nowrap",
                  active
                    ? "text-white"
                    : "bg-slate-100 text-slate-400 hover:bg-slate-200",
                ].join(" ")}
                style={active ? { backgroundColor: g.brandColor } : undefined}
              >
                {g.label}
              </button>
            )
          })}
        </div>

        {/* Line / Bar toggle */}
        <Tabs
          value={chartType}
          onValueChange={(v) => setChartType(v as "line" | "bar")}
        >
          <TabsList className="h-7">
            <TabsTrigger value="line" className="h-5 px-2">
              <ChartLine size={13} />
            </TabsTrigger>
            <TabsTrigger value="bar" className="h-5 px-2">
              <ChartColumnBig size={13} />
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Shared legend */}
      <SharedLegend brandName={brandName} competitorName={competitorName} />

      {/* Sub-charts, one per active group */}
      {activeGroups.map((g, idx) => (
        <div key={g.key}>
          {idx > 0 && <div className="h-px w-full bg-blue-100 my-4" />}
          <p
            className="text-xs font-semibold uppercase tracking-wide mb-1"
            style={{ color: g.brandColor }}
          >
            {g.label}
          </p>
          <SubChart
            group={g}
            data={chartData}
            chartType={chartType}
            brandName={brandName}
            competitorName={competitorName}
          />
        </div>
      ))}
    </div>
  )
}
