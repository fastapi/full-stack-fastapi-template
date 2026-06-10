"use client";

import type { ReactNode } from "react";
import { AlertTriangle, Clock, FileCheck2 } from "lucide-react";
import { useTranslations } from "next-intl";
import Pill from "@/components/ui/Pill";
import { DOCS, type DocStatus } from "@/lib/data";

const FEED_ICO: Record<DocStatus, ReactNode> = {
  done: <FileCheck2 size={16} />,
  proc: <Clock size={16} />,
  fail: <AlertTriangle size={16} />,
};

export default function HistoryView() {
  const t = useTranslations("pages.history");
  const log = DOCS.concat(
    DOCS.slice(0, 6).map((d, i) => ({
      ...d,
      id: d.id + "-b",
      date: "2026-06-0" + (4 - (i % 3)) + " 08:1" + i,
    })),
  );

  return (
    <div className="panel">
      <div className="panel-head">
        <div>
          <h3>{t("title")}</h3>
          <div className="sub">{t("sub")}</div>
        </div>
      </div>
      <div className="log-list">
        {log.map((d, i) => (
          <div className="feed-item" key={d.id + i}>
            <span className={`feed-ico ${d.status}`}>{FEED_ICO[d.status]}</span>
            <div className="feed-main">
              <div className="fn">{d.name}</div>
              <div className="meta">
                {d.id} · {d.size} · {d.date}
              </div>
            </div>
            <Pill status={d.status} />
          </div>
        ))}
      </div>
    </div>
  );
}
