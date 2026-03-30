import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { getAuthToken } from "@/clients/auth-helper"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import QueryDrillDown from "./QueryDrillDown"

// ── Types ────────────────────────────────────────────────────────────────────

interface SignalDetailResponse {
  signal: {
    type: string
    severity: string
    score: number
    created_date: string
  }
  why_fired: {
    explanation: string
    metrics: Array<{
      label: string
      value: string
      from?: string
      to?: string
      status: string
    }>
  }
  competitors: Array<{
    name: string
    sov: number
    ssi: number
    position_strength: number
    trend_7d: number
    is_target?: boolean
    is_top_threat?: boolean
  }>
  recommendations: Array<{
    priority: number
    title: string
    detail: string
    action_type: string
  }>
}

interface Props {
  selectedSignal: { signal_type: string; segment: string; date: string } | null
  brandId: number
}

// ── API helpers ──────────────────────────────────────────────────────────────

const API_BASE_URL = import.meta.env.VITE_API_URL ?? ""
const API_PREFIX = "/api/v1"

async function fetchSignalDetail(
  signal_type: string,
  brand_id: number,
  segment: string,
  date: string,
): Promise<SignalDetailResponse> {
  const token = getAuthToken()
  const params = new URLSearchParams({
    brand_id: String(brand_id),
    segment,
    date,
  })
  const url = `${API_BASE_URL}${API_PREFIX}/insights/signal/${encodeURIComponent(signal_type)}?${params.toString()}`
  const res = await fetch(url, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      "Content-Type": "application/json",
    },
  })
  if (!res.ok) {
    throw new Error(`Failed to fetch signal detail: ${res.status}`)
  }
  return res.json() as Promise<SignalDetailResponse>
}

// ── Status color helpers ─────────────────────────────────────────────────────

function metricValueColor(status: string): string {
  switch (status) {
    case "critical":
      return "text-red-400"
    case "warning":
    case "fragile":
      return "text-amber-400"
    default:
      return "text-slate-300"
  }
}

// ── Sub-components ───────────────────────────────────────────────────────────

function SkeletonDetail() {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="rounded-lg bg-slate-900 border border-slate-700 p-4 space-y-3">
          <div className="h-4 w-40 bg-slate-700 rounded animate-pulse" />
          <div className="h-3 w-full bg-slate-800 rounded animate-pulse" />
          <div className="h-3 w-5/6 bg-slate-800 rounded animate-pulse" />
          <div className="flex gap-3 mt-2">
            {[1, 2, 3, 4].map((j) => (
              <div key={j} className="flex-1 h-14 bg-slate-800 rounded animate-pulse" />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

interface MetricTileProps {
  label: string
  value: string
  status: string
}

function MetricTile({ label, value, status }: MetricTileProps) {
  return (
    <div className="flex-1 min-w-0 bg-slate-800 rounded-lg p-3 flex flex-col gap-1">
      <span className={`text-lg font-bold leading-tight ${metricValueColor(status)}`}>
        {value}
      </span>
      <span className="text-[11px] text-slate-500 leading-tight">{label}</span>
    </div>
  )
}

function TrendValue({ value }: { value: number }) {
  if (value > 0) {
    return (
      <span className="text-green-400 text-xs">
        +{value.toFixed(1)}%
      </span>
    )
  }
  if (value < 0) {
    return (
      <span className="text-red-400 text-xs">
        {value.toFixed(1)}%
      </span>
    )
  }
  return <span className="text-slate-500 text-xs">0.0%</span>
}

interface ActionItemProps {
  rec: SignalDetailResponse["recommendations"][number]
  index: number
  brandId: number
  selectedSignal: NonNullable<Props["selectedSignal"]>
}

function ActionItem({ rec, index, brandId, selectedSignal }: ActionItemProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="py-3 border-b border-slate-800 last:border-0">
      <div className="flex gap-3">
        <span className="shrink-0 w-5 h-5 rounded-full bg-slate-700 text-slate-300 text-[11px] font-bold flex items-center justify-center mt-0.5">
          {index + 1}
        </span>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-slate-200 leading-snug">{rec.title}</p>
          <p className="text-xs text-slate-500 mt-0.5 leading-snug">{rec.detail}</p>
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="mt-1.5 text-[11px] text-blue-400 hover:text-blue-300 transition-colors"
          >
            {expanded ? "Hide ▴" : "View queries ▾"}
          </button>
          {expanded && (
            <div className="mt-3">
              <QueryDrillDown
                signal_type={selectedSignal.signal_type}
                brand_id={brandId}
                segment={selectedSignal.segment}
                date={selectedSignal.date}
                action_type={rec.action_type}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ── Main component ───────────────────────────────────────────────────────────

export function SignalDetail({ selectedSignal, brandId }: Props) {
  const { data, isLoading } = useQuery<SignalDetailResponse>({
    queryKey: ["signal-detail", selectedSignal],
    queryFn: () => {
      if (!selectedSignal) throw new Error("No signal selected")
      return fetchSignalDetail(
        selectedSignal.signal_type,
        brandId,
        selectedSignal.segment,
        selectedSignal.date,
      )
    },
    enabled: selectedSignal !== null,
  })

  if (!selectedSignal) {
    return (
      <div className="flex-1 flex items-center justify-center text-slate-500 text-sm">
        Select a signal to see details.
      </div>
    )
  }

  if (isLoading || !data) {
    return <SkeletonDetail />
  }

  const { why_fired, competitors, recommendations } = data

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {/* Section 1: Why Fired */}
      <Card className="bg-slate-900 border-slate-700 text-slate-200">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-semibold text-slate-300">
            Why This Signal Fired
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-slate-400 leading-relaxed">{why_fired.explanation}</p>
          {why_fired.metrics.length > 0 && (
            <div className="flex gap-3 flex-wrap">
              {why_fired.metrics.map((m) => (
                <MetricTile
                  key={m.label}
                  label={m.label}
                  value={m.value}
                  status={m.status}
                />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Section 2: Competitor Breakdown */}
      {competitors.length > 0 && (
        <Card className="bg-slate-900 border-slate-700 text-slate-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold text-slate-300">
              Competitor Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="px-4 py-2 text-left text-slate-500 font-medium">Brand</th>
                  <th className="px-3 py-2 text-right text-slate-500 font-medium">SOV</th>
                  <th className="px-3 py-2 text-right text-slate-500 font-medium">SSI</th>
                  <th className="px-3 py-2 text-right text-slate-500 font-medium">Pos. Strength</th>
                  <th className="px-3 py-2 text-right text-slate-500 font-medium">7d Trend</th>
                </tr>
              </thead>
              <tbody>
                {competitors.map((c) => {
                  const rowBorder = c.is_target
                    ? "border-l-2 border-blue-500"
                    : c.is_top_threat
                      ? "border-l-2 border-red-500"
                      : ""
                  return (
                    <tr
                      key={c.name}
                      className={`border-b border-slate-800 last:border-0 ${rowBorder}`}
                    >
                      <td className="px-4 py-2 text-slate-200 font-medium">{c.name}</td>
                      <td className="px-3 py-2 text-right text-slate-400">
                        {c.sov.toFixed(1)}%
                      </td>
                      <td className="px-3 py-2 text-right text-slate-400">
                        {c.ssi.toFixed(1)}%
                      </td>
                      <td className="px-3 py-2 text-right text-slate-400">
                        {c.position_strength.toFixed(1)}%
                      </td>
                      <td className="px-3 py-2 text-right">
                        <TrendValue value={c.trend_7d} />
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}

      {/* Section 3: Recommended Actions */}
      {recommendations.length > 0 && (
        <Card className="bg-slate-900 border-slate-700 text-slate-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold text-slate-300">
              Recommended Actions
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            {recommendations.map((rec, i) => (
              <ActionItem
                key={rec.action_type}
                rec={rec}
                index={i}
                brandId={brandId}
                selectedSignal={selectedSignal}
              />
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
