import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { getAuthToken } from "@/clients/auth-helper"
import { dashboardAPI } from "@/clients/dashboard"
import SignalCommandCenter from "./SignalCommandCenter"
import SignalDetail from "./SignalDetail"

// ── Types ────────────────────────────────────────────────────────────────────

interface SignalSummaryItem {
  signal_type: string
  severity: string
  business_meaning: string
  score: number
  top_competitor: string | null
  created_date: string
}

interface OverviewResponse {
  date: string
  summary: { high: number; medium: number; low: number }
  categories: {
    competitive_position: SignalSummaryItem[]
    momentum_acceleration: SignalSummaryItem[]
    structural_strength: SignalSummaryItem[]
    risk_instability: SignalSummaryItem[]
  }
}

interface SelectedSignal {
  signal_type: string
  segment: string
  date: string
}

// ── API helpers ──────────────────────────────────────────────────────────────

const API_BASE_URL = import.meta.env.VITE_API_URL ?? ""
const API_PREFIX = "/api/v1"

async function fetchOverview(
  brand_id: number,
  segment: string,
): Promise<OverviewResponse> {
  const token = getAuthToken()
  const params = new URLSearchParams({ brand_id: String(brand_id), segment })
  const url = `${API_BASE_URL}${API_PREFIX}/insights/overview?${params.toString()}`
  const res = await fetch(url, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      "Content-Type": "application/json",
    },
  })
  if (!res.ok) {
    throw new Error(`Failed to fetch insights overview: ${res.status}`)
  }
  return res.json() as Promise<OverviewResponse>
}

// ── Component ────────────────────────────────────────────────────────────────

export default function ActionableInsights() {
  const [selectedSignal, setSelectedSignal] = useState<SelectedSignal | null>(
    null,
  )

  // Fetch brands to get brand_id
  const { data: brandsData } = useQuery({
    queryKey: ["user-brands-insights"],
    queryFn: () => dashboardAPI.getUserBrands(),
  })

  const brand = brandsData?.brands?.[0]
  const brandId = brand ? Number(brand.brand_id) : null
  const segment = ""

  // Fetch overview once brand is available
  const { data: overview, isLoading: overviewLoading } =
    useQuery({
      queryKey: ["insights-overview", brandId, segment],
      queryFn: () => fetchOverview(brandId!, segment),
      enabled: brandId !== null,
    })

  return (
    <div className="flex h-full min-h-0 overflow-hidden">
      {/* Left: Command Center */}
      <div className="w-60 shrink-0 overflow-y-auto border-r border-slate-700">
        <SignalCommandCenter
          overview={overviewLoading ? undefined : overview}
          selectedSignal={selectedSignal}
          onSelectSignal={setSelectedSignal}
        />
      </div>

      {/* Right: Signal Detail */}
      <div className="flex-1 overflow-y-auto">
        {brandId !== null ? (
          <SignalDetail selectedSignal={selectedSignal} brandId={brandId} />
        ) : (
          <div className="flex h-full items-center justify-center text-slate-500">
            Loading...
          </div>
        )}
      </div>
    </div>
  )
}
