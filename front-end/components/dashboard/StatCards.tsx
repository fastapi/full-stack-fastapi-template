"use client";

import type { ReactNode } from "react";
import { FileCheck2, FileSpreadsheet, HardDrive, TrendingDown, TrendingUp, XCircle } from "lucide-react";
import { useTranslations } from "next-intl";
import { useCount } from "@/components/dashboard/hooks";

interface StatDef {
  ico: ReactNode;
  tone: "" | "ok" | "bad" | "am";
  val: number;
  decimals?: number;
  suffix?: string;
  capKey: "cardDocuments" | "cardExports" | "cardFailed" | "cardStorage";
  delta: string;
  up: boolean;
}

const STATS: StatDef[] = [
  { ico: <FileCheck2 size={18} />, tone: "", val: 10248, capKey: "cardDocuments", delta: "+12.4%", up: true },
  { ico: <FileSpreadsheet size={18} />, tone: "ok", val: 9961, capKey: "cardExports", delta: "+11.8%", up: true },
  { ico: <XCircle size={18} />, tone: "bad", val: 287, capKey: "cardFailed", delta: "-3.1%", up: false },
  { ico: <HardDrive size={18} />, tone: "am", val: 248, suffix: " MB", capKey: "cardStorage", delta: "+6.2%", up: true },
];

function StatCard({ def }: { def: StatDef }) {
  const t = useTranslations("overview");
  const num = useCount(def.val, def.decimals ?? 0);
  return (
    <div className="stat-card">
      <div className="row1">
        <span className={`sc-ico ${def.tone}`}>{def.ico}</span>
        <span className={`delta ${def.up ? "up" : "down"}`}>
          {def.up ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
          {def.delta}
        </span>
      </div>
      <div className="val">
        {num}
        {def.suffix}
      </div>
      <div className="cap">{t(def.capKey)}</div>
    </div>
  );
}

export default function StatCards() {
  return (
    <div className="stat-grid">
      {STATS.map((def) => (
        <StatCard key={def.capKey} def={def} />
      ))}
    </div>
  );
}
