import { useQuery } from "@tanstack/react-query"
import { getAuthToken } from "@/clients/auth-helper"

// ── Types ────────────────────────────────────────────────────────────────────

interface QueryDrillDownResponse {
  queries: Array<{
    prompt_text: string
    brand_rank_today: number
    brand_rank_7d_ago: number
    rank_change: number
    top_competitor_today: string | null
    top_competitor_rank: number | null
  }>
}

interface Props {
  signal_type: string
  brand_id: number
  segment: string
  date: string
  action_type: string
}

// ── API helpers ──────────────────────────────────────────────────────────────

const API_BASE_URL = import.meta.env.VITE_API_URL ?? ""
const API_PREFIX = "/api/v1"

async function fetchQueryDrillDown(
  signal_type: string,
  brand_id: number,
  segment: string,
  date: string,
  action_type: string,
): Promise<QueryDrillDownResponse> {
  const token = getAuthToken()
  const params = new URLSearchParams({
    brand_id: String(brand_id),
    segment,
    date,
    action_type,
  })
  const url = `${API_BASE_URL}${API_PREFIX}/insights/signal/${encodeURIComponent(signal_type)}/queries?${params.toString()}`
  const res = await fetch(url, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      "Content-Type": "application/json",
    },
  })
  if (!res.ok) {
    throw new Error(`Failed to fetch query drill-down: ${res.status}`)
  }
  return res.json() as Promise<QueryDrillDownResponse>
}

// ── Rank change helpers ──────────────────────────────────────────────────────

function rankChangeColor(change: number): string {
  if (change < 0) return "text-red-400"
  if (change > 0) return "text-green-400"
  return "text-slate-500"
}

function rankChangeLabel(change: number): string {
  if (change > 0) return `+${change}`
  if (change < 0) return String(change)
  return "0"
}

// ── Main component ───────────────────────────────────────────────────────────

export default function QueryDrillDown({
  signal_type,
  brand_id,
  segment,
  date,
  action_type,
}: Props) {
  const { data, isLoading, isError } = useQuery<QueryDrillDownResponse>({
    queryKey: ["query-drilldown", signal_type, brand_id, segment, date, action_type],
    queryFn: () => fetchQueryDrillDown(signal_type, brand_id, segment, date, action_type),
    enabled: true,
  })

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 py-3 text-slate-500 text-xs">
        <svg
          className="animate-spin h-3.5 w-3.5 text-slate-400"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
          />
        </svg>
        Loading queries…
      </div>
    )
  }

  if (isError) {
    return (
      <div className="py-3 text-xs text-red-400">
        Failed to load queries. Please try again.
      </div>
    )
  }

  if (!data || data.queries.length === 0) {
    return (
      <div className="py-3 text-xs text-slate-500">
        No query data available.
      </div>
    )
  }

  return (
    <div className="rounded-lg border border-slate-700 overflow-hidden">
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-slate-700 bg-slate-800/60">
            <th className="px-3 py-2 text-left text-slate-500 font-medium">Query</th>
            <th className="px-3 py-2 text-right text-slate-500 font-medium">Brand Rank</th>
            <th className="px-3 py-2 text-right text-slate-500 font-medium">7d Ago</th>
            <th className="px-3 py-2 text-right text-slate-500 font-medium">Change</th>
            <th className="px-3 py-2 text-left text-slate-500 font-medium">Top Competitor</th>
          </tr>
        </thead>
        <tbody>
          {data.queries.map((q, i) => (
            <tr
              // biome-ignore lint/suspicious/noArrayIndexKey: stable list from API
              key={i}
              className="border-b border-slate-800 last:border-0 hover:bg-slate-800/40 transition-colors"
            >
              <td
                className="px-3 py-2 text-slate-300 max-w-[200px] truncate"
                title={q.prompt_text}
              >
                {q.prompt_text}
              </td>
              <td className="px-3 py-2 text-right text-slate-400">{q.brand_rank_today}</td>
              <td className="px-3 py-2 text-right text-slate-400">{q.brand_rank_7d_ago}</td>
              <td className={`px-3 py-2 text-right font-semibold ${rankChangeColor(q.rank_change)}`}>
                {rankChangeLabel(q.rank_change)}
              </td>
              <td className="px-3 py-2 text-slate-400 max-w-[140px] truncate">
                {q.top_competitor_today
                  ? `${q.top_competitor_today}${q.top_competitor_rank !== null ? ` (#${q.top_competitor_rank})` : ""}`
                  : <span className="text-slate-600">—</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
