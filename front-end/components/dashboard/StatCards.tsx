"use client";

import type { ReactNode } from "react";
import { FileCheck2, FileSpreadsheet, HardDrive, Wallet } from "lucide-react";
import { useTranslations } from "next-intl";
import { useCount } from "@/components/dashboard/hooks";
import type { UserStorageStatPublic } from "@/lib/client";

interface StatDef {
  ico: ReactNode;
  tone: "" | "ok" | "bad" | "am";
  val: number;
  decimals?: number;
  suffix?: string;
  capKey: "cardDocuments" | "cardPages" | "cardStorage" | "cardBalance";
}

function StatCard({ def }: { def: StatDef }) {
  const t = useTranslations("overview");
  const num = useCount(def.val, def.decimals ?? 0);
  return (
    <div className="stat-card">
      <div className="row1">
        <span className={`sc-ico ${def.tone}`}>{def.ico}</span>
      </div>
      <div className="val">
        {num}
        {def.suffix}
      </div>
      <div className="cap">{t(def.capKey)}</div>
    </div>
  );
}

export interface StatCardsProps {
  stat: UserStorageStatPublic | null;
}

export default function StatCards({ stat }: StatCardsProps) {
  const stats: StatDef[] = [
    { ico: <FileCheck2 size={18} />, tone: "", val: stat?.file_count ?? 0, capKey: "cardDocuments" },
    { ico: <FileSpreadsheet size={18} />, tone: "ok", val: stat?.total_pages ?? 0, capKey: "cardPages" },
    {
      ico: <HardDrive size={18} />,
      tone: "am",
      val: (stat?.total_size ?? 0) / 1024 / 1024,
      decimals: 1,
      suffix: " MB",
      capKey: "cardStorage",
    },
    { ico: <Wallet size={18} />, tone: "", val: stat?.balance ?? 0, suffix: " ₫", capKey: "cardBalance" },
  ];

  return (
    <div className="stat-grid">
      {stats.map((def) => (
        <StatCard key={def.capKey} def={def} />
      ))}
    </div>
  );
}
