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

interface Props {
  overview: OverviewResponse | undefined
  selectedSignal: SelectedSignal | null
  onSelectSignal: (signal: SelectedSignal) => void
}

function humanizeSignalType(signalType: string): string {
  return signalType
    .replace(/_signal$/, "")
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ")
}

const severityStyles: Record<string, string> = {
  High: "bg-red-950 border border-red-500 text-red-400",
  Medium: "bg-amber-950 border border-amber-500 text-amber-400",
  Low: "bg-green-950 border border-green-500 text-green-400",
}

const summarySeverityStyles: Record<
  string,
  { badge: string; label: string }
> = {
  high: {
    badge: "bg-red-950 border border-red-500 text-red-400",
    label: "HIGH",
  },
  medium: {
    badge: "bg-amber-950 border border-amber-500 text-amber-400",
    label: "MEDIUM",
  },
  low: {
    badge: "bg-green-950 border border-green-500 text-green-400",
    label: "LOW",
  },
}

const categories: Array<{
  key: keyof OverviewResponse["categories"]
  label: string
}> = [
  { key: "competitive_position", label: "COMPETITIVE" },
  { key: "momentum_acceleration", label: "MOMENTUM" },
  { key: "structural_strength", label: "STRUCTURAL" },
  { key: "risk_instability", label: "RISK" },
]

interface SignalItemProps {
  item: SignalSummaryItem
  overviewDate: string
  isSelected: boolean
  onSelect: (signal: SelectedSignal) => void
}

function SignalItem({
  item,
  overviewDate,
  isSelected,
  onSelect,
}: SignalItemProps) {
  const handleClick = () => {
    onSelect({
      signal_type: item.signal_type,
      segment: overviewDate,
      date: item.created_date,
    })
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      className={`w-full text-left px-3 py-2 cursor-pointer transition-colors ${
        isSelected
          ? "bg-blue-900 border-l-2 border-blue-500"
          : "hover:bg-slate-800 border-l-2 border-transparent"
      }`}
    >
      <div className="flex items-center gap-2 mb-0.5">
        <span className="text-slate-200 text-xs font-medium truncate flex-1">
          {humanizeSignalType(item.signal_type)}
        </span>
        <span
          className={`text-[10px] font-semibold px-1.5 py-0.5 rounded shrink-0 ${
            severityStyles[item.severity] ?? severityStyles.Low
          }`}
        >
          {item.severity.toUpperCase()}
        </span>
      </div>
      <p className="text-slate-500 text-[11px] truncate leading-tight">
        {item.business_meaning}
      </p>
    </button>
  )
}

function SkeletonPanel() {
  return (
    <div className="w-60 shrink-0 bg-slate-900 border-r border-slate-700 flex flex-col">
      <div className="px-4 py-3 border-b border-slate-700">
        <div className="h-3 w-24 bg-slate-700 rounded animate-pulse mb-3" />
        <div className="flex gap-2">
          <div className="h-5 w-16 bg-slate-700 rounded animate-pulse" />
          <div className="h-5 w-20 bg-slate-700 rounded animate-pulse" />
          <div className="h-5 w-14 bg-slate-700 rounded animate-pulse" />
        </div>
      </div>
      <div className="flex-1 overflow-y-auto">
        {[1, 2, 3].map((i) => (
          <div key={i} className="px-3 py-2 space-y-1.5">
            <div className="h-2 w-20 bg-slate-700 rounded animate-pulse" />
            <div className="h-8 bg-slate-800 rounded animate-pulse" />
            <div className="h-8 bg-slate-800 rounded animate-pulse" />
          </div>
        ))}
      </div>
    </div>
  )
}

export function SignalCommandCenter({
  overview,
  selectedSignal,
  onSelectSignal,
}: Props) {
  if (!overview) {
    return <SkeletonPanel />
  }

  const { summary, categories: cats, date } = overview

  return (
    <div className="w-60 shrink-0 bg-slate-900 border-r border-slate-700 flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-700">
        <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest mb-2">
          Today's Alerts
        </p>
        <div className="flex flex-wrap gap-1.5">
          {(["high", "medium", "low"] as const).map((level) => {
            const count = summary[level]
            const style = summarySeverityStyles[level]
            return (
              <span
                key={level}
                className={`text-[11px] font-semibold px-2 py-0.5 rounded ${style.badge}`}
              >
                {count} {style.label}
              </span>
            )
          })}
        </div>
      </div>

      {/* Signal List */}
      <div className="flex-1 overflow-y-auto">
        {categories.map(({ key, label }) => {
          const signals = cats[key]
          if (!signals || signals.length === 0) return null

          return (
            <div key={key}>
              <p className="px-3 pt-3 pb-1 text-[10px] font-semibold text-slate-500 uppercase tracking-widest">
                {label}
              </p>
              {signals.map((item) => {
                const isSelected =
                  selectedSignal?.signal_type === item.signal_type &&
                  selectedSignal?.date === item.created_date

                return (
                  <SignalItem
                    key={`${item.signal_type}-${item.created_date}`}
                    item={item}
                    overviewDate={date}
                    isSelected={isSelected}
                    onSelect={onSelectSignal}
                  />
                )
              })}
            </div>
          )
        })}
      </div>
    </div>
  )
}
