"use client";

import type { ReactNode } from "react";
import { AlertTriangle, Clock, FileCheck2 } from "lucide-react";
import { useTranslations } from "next-intl";
import type { DocRow, DocStatus } from "@/lib/data";

const FEED_ICO: Record<DocStatus, ReactNode> = {
  done: <FileCheck2 size={16} />,
  proc: <Clock size={16} />,
  fail: <AlertTriangle size={16} />,
};

export interface ActivityFeedProps {
  items: DocRow[];
}

export default function ActivityFeed({ items }: ActivityFeedProps) {
  const t = useTranslations("overview");
  const metaFor = (status: DocStatus) =>
    status === "done" ? t("feedDone") : status === "proc" ? t("feedProc") : t("feedFail");

  if (items.length === 0) {
    return <div className="fq-empty">{t("feedEmpty")}</div>;
  }

  return (
    <div className="feed">
      {items.map((d) => (
        <div className="feed-item" key={d.id}>
          <span className={`feed-ico ${d.status}`}>{FEED_ICO[d.status]}</span>
          <div className="feed-main">
            <div className="fn">{d.name}</div>
            <div className="meta">
              {metaFor(d.status)}
              {d.pages > 0 && <> · {t("pages", { count: d.pages })}</>}
            </div>
          </div>
          <span className="feed-time">{d.date}</span>
        </div>
      ))}
    </div>
  );
}
