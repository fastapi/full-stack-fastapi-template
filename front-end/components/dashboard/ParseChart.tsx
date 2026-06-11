"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useTranslations } from "next-intl";
import type { VolumePoint } from "@/lib/data";

const FAILED = "oklch(0.68 0.17 25)";

interface TipPayload {
  dataKey?: string | number;
  color?: string;
  value?: number;
}
interface TipProps {
  active?: boolean;
  payload?: TipPayload[];
  label?: string | number;
  labels: { parsed: string; failed: string };
}

function ChartTooltip({ active, payload, label, labels }: TipProps) {
  if (!active || !payload || !payload.length) return null;
  return (
    <div className="rc-tip">
      <div className="t-label">{label} · 2026</div>
      {payload.map((p) => (
        <div className="t-row" key={String(p.dataKey)}>
          <i style={{ background: p.color }} />
          {p.dataKey === "parsed" ? labels.parsed : labels.failed} —{" "}
          {(p.value ?? 0).toLocaleString()}
        </div>
      ))}
    </div>
  );
}

export interface ParseChartProps {
  data: VolumePoint[];
  accent?: string;
}

export default function ParseChart({ data, accent = "#2FCB91" }: ParseChartProps) {
  const t = useTranslations("overview");
  const labels = { parsed: t("legendParsed"), failed: t("legendFailed") };
  return (
    <ResponsiveContainer width="100%" height={262}>
      <AreaChart data={data} margin={{ top: 8, right: 6, left: -18, bottom: 0 }}>
        <defs>
          <linearGradient id="gParsed" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={accent} stopOpacity={0.35} />
            <stop offset="100%" stopColor={accent} stopOpacity={0} />
          </linearGradient>
          <linearGradient id="gFailed" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={FAILED} stopOpacity={0.28} />
            <stop offset="100%" stopColor={FAILED} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="var(--line-soft)" vertical={false} />
        <XAxis
          dataKey="day"
          tick={{ fill: "var(--fg-dim)", fontSize: 11, fontFamily: "var(--font-mono)" }}
          axisLine={false}
          tickLine={false}
          interval={4}
        />
        <YAxis
          tick={{ fill: "var(--fg-dim)", fontSize: 11, fontFamily: "var(--font-mono)" }}
          axisLine={false}
          tickLine={false}
          width={48}
        />
        <Tooltip
          content={(props) => (
            <ChartTooltip {...(props as unknown as Omit<TipProps, "labels">)} labels={labels} />
          )}
          cursor={{ stroke: accent, strokeOpacity: 0.45, strokeWidth: 1 }}
        />
        <Area type="monotone" dataKey="failed" stroke={FAILED} strokeWidth={1.5} fill="url(#gFailed)" isAnimationActive={false} />
        <Area type="monotone" dataKey="parsed" stroke={accent} strokeWidth={2} fill="url(#gParsed)" isAnimationActive={false} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
