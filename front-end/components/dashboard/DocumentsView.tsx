"use client";

import { useState } from "react";
import { Calendar, Download, Eye, FileText, Image as ImageIcon, Search, Trash2 } from "lucide-react";
import { useTranslations } from "next-intl";
import Pill from "@/components/ui/Pill";
import { DOCS, type DocRow, type DocStatus } from "@/lib/data";

type StatusFilter = "all" | DocStatus;
type RangeFilter = "7d" | "30d" | "all";

export default function DocumentsView() {
  const t = useTranslations("documents");
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<StatusFilter>("all");
  const [range, setRange] = useState<RangeFilter>("30d");
  const [docs, setDocs] = useState<DocRow[]>(DOCS);

  const filtered = docs.filter((d) => {
    const mq = query.trim().toLowerCase();
    const okQ = !mq || d.name.toLowerCase().includes(mq) || d.id.toLowerCase().includes(mq);
    const okS = status === "all" || d.status === status;
    return okQ && okS;
  });

  const remove = (id: string) => setDocs((p) => p.filter((d) => d.id !== id));

  const statusOptions: [StatusFilter, string][] = [
    ["all", t("filterAll")],
    ["done", t("filterDone")],
    ["proc", t("filterProc")],
    ["fail", t("filterFail")],
  ];
  const rangeOptions: [RangeFilter, string][] = [
    ["7d", t("range7d")],
    ["30d", t("range30d")],
    ["all", t("rangeAll")],
  ];

  return (
    <div>
      <div className="toolbar">
        <div className="search">
          <Search size={15} />
          <input
            placeholder={t("searchPlaceholder")}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            aria-label={t("searchPlaceholder")}
          />
        </div>
        <div className="seg">
          {statusOptions.map(([k, l]) => (
            <button key={k} className={status === k ? "on cy" : ""} onClick={() => setStatus(k)}>
              {l}
            </button>
          ))}
        </div>
        <div className="seg">
          {rangeOptions.map(([k, l]) => (
            <button key={k} className={range === k ? "on" : ""} onClick={() => setRange(k)}>
              {k === "all" ? (
                <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                  <Calendar size={12} /> {l}
                </span>
              ) : (
                l
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="table-wrap">
        <table className="tbl">
          <thead>
            <tr>
              <th>{t("colFilename")}</th>
              <th>{t("colJobId")}</th>
              <th>{t("colType")}</th>
              <th>{t("colUploaded")}</th>
              <th>{t("colStatus")}</th>
              <th style={{ textAlign: "right" }}>{t("colActions")}</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr className="empty-row">
                <td colSpan={6}>{t("empty")}</td>
              </tr>
            )}
            {filtered.map((d) => (
              <tr key={d.id}>
                <td>
                  <div className="fname">
                    <span className={`ftype ${d.type}`}>
                      {d.type === "pdf" ? <FileText size={15} /> : <ImageIcon size={15} />}
                    </span>
                    <span>
                      <div className="nm">{d.name}</div>
                      <div className="sz">
                        {d.size} · {d.pages} {d.pages > 1 ? "pages" : "page"}
                      </div>
                    </span>
                  </div>
                </td>
                <td className="mono-cell">{d.id}</td>
                <td className="mono-cell">{d.type === "pdf" ? t("typePdf") : t("typeImage")}</td>
                <td className="mono-cell">{d.date}</td>
                <td>
                  {d.status === "proc" ? (
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <Pill status="proc" />
                      <div className="mini-prog">
                        <i style={{ width: `${d.progress ?? 30}%` }} />
                      </div>
                    </div>
                  ) : (
                    <Pill status={d.status} />
                  )}
                </td>
                <td>
                  <div className="row-actions" style={{ justifyContent: "flex-end" }}>
                    <button className="dl" title={t("download")} aria-label={t("download")} disabled={d.status !== "done"}>
                      <Download size={15} />
                    </button>
                    <button title={t("view")} aria-label={t("view")}>
                      <Eye size={15} />
                    </button>
                    <button className="del" title={t("delete")} aria-label={t("delete")} onClick={() => remove(d.id)}>
                      <Trash2 size={15} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="table-foot">
          <span>{t("showing", { shown: filtered.length, total: docs.length })}</span>
          <span>{t("storage")}</span>
        </div>
      </div>
    </div>
  );
}
