export const CHART_COLORS = {
  blue: "#2563eb",
  purple: "#7c3aed",
  green: "#10b981",
  amber: "#f59e0b",
  red: "#ef4444",
  teal: "#14b8a6",
  slate: "#94a3b8",
  indigoLight: "#818cf8",
  greenLight: "#34d399",
  orangeLight: "#fb923c",
}

export const CHART_PALETTE = [
  CHART_COLORS.blue,
  CHART_COLORS.purple,
  CHART_COLORS.green,
  CHART_COLORS.amber,
  CHART_COLORS.red,
  CHART_COLORS.teal,
]

export const axisProps = {
  tick: { fontSize: 11, fill: "#94a3b8" },
  axisLine: false,
  tickLine: false,
}

export const gridProps = {
  strokeDasharray: "3 3",
  stroke: "#e2e8f0",
  vertical: false,
}

export const tooltipClasses = {
  container:
    "bg-slate-900 border border-slate-700 rounded-xl shadow-xl p-3 min-w-[170px]",
  label: "text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wide",
  row: "flex items-center justify-between gap-4 text-xs py-0.5",
  name: "text-slate-300",
  value: "font-semibold text-white",
  note: "text-xs text-slate-500 mt-2",
}

export const legendClasses = {
  container: "flex flex-wrap justify-center gap-3 mt-2",
  item: "flex items-center gap-2 text-xs cursor-pointer transition-opacity",
  label: "text-slate-600",
}

export const formatShortDate = (isoDate: string): string => {
  const date = new Date(isoDate)
  return `${date.getMonth() + 1}/${date.getDate()}`
}
