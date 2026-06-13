"use client";

import { useCallback, useEffect, useState } from "react";
import { Download, Eye, FileText, Image as ImageIcon, RefreshCw, Search } from "lucide-react";
import { useTranslations } from "next-intl";
import Pill from "@/components/ui/Pill";
import PreviewModal from "@/components/dashboard/PreviewModal";
import { apiMessage } from "@/lib/api";
import { FilesService } from "@/lib/client";
import { downloadExport, toDocRow } from "@/lib/files";
import type { DocRow, DocStatus } from "@/lib/data";

type StatusFilter = "all" | DocStatus;

interface PreviewState {
  name: string;
  columns: string[];
  rows: Record<string, unknown>[];
  markdownUrl: string | null;
  loading: boolean;
  error: string | null;
}

export default function DocumentsView() {
  const t = useTranslations("documents");
  const tc = useTranslations("common");
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<StatusFilter>("all");
  const [docs, setDocs] = useState<DocRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [preview, setPreview] = useState<PreviewState | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const files = await FilesService.listFiles({ limit: 100 });
      setDocs(files.map(toDocRow));
    } catch (err) {
      setError(apiMessage(err));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const refresh = () => {
    setRefreshing(true);
    void load();
  };

  const download = async (d: DocRow) => {
    setBusyId(d.id);
    try {
      await downloadExport(d.id, d.name, "xlsx");
    } catch (err) {
      setError(apiMessage(err));
    } finally {
      setBusyId(null);
    }
  };

  const viewResult = async (d: DocRow) => {
    setBusyId(d.id);
    setPreview({ name: d.name, columns: [], rows: [], markdownUrl: null, loading: true, error: null });
    try {
      const res = await FilesService.previewFileResult({ fileId: d.id });
      setPreview({
        name: res.filename || d.name,
        columns: res.columns,
        rows: res.rows,
        markdownUrl: res.markdown_url ?? null,
        loading: false,
        error: null,
      });
    } catch (err) {
      setPreview((p) => (p ? { ...p, loading: false, error: apiMessage(err) } : p));
    } finally {
      setBusyId(null);
    }
  };

  const filtered = docs.filter((d) => {
    const mq = query.trim().toLowerCase();
    const okQ = !mq || d.name.toLowerCase().includes(mq) || d.id.toLowerCase().includes(mq);
    const okS = status === "all" || d.status === status;
    return okQ && okS;
  });

  const statusOptions: [StatusFilter, string][] = [
    ["all", t("filterAll")],
    ["done", t("filterDone")],
    ["proc", t("filterProc")],
    ["fail", t("filterFail")],
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
          <button onClick={refresh} disabled={refreshing} aria-label={t("refresh")}>
            <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
              <RefreshCw size={12} className={refreshing ? "spin" : ""} /> {t("refresh")}
            </span>
          </button>
        </div>
      </div>

      {error && <div className="field-error">{error}</div>}

      <div className="table-wrap">
        <table className="tbl">
          <thead>
            <tr>
              <th>{t("colFilename")}</th>
              <th>{t("colJobId")}</th>
              <th>{t("colType")}</th>
              <th>{t("colModel")}</th>
              <th>{t("colUploaded")}</th>
              <th>{t("colStatus")}</th>
              <th style={{ textAlign: "right" }}>{t("colActions")}</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr className="empty-row">
                <td colSpan={7}>{tc("loading")}</td>
              </tr>
            )}
            {!loading && filtered.length === 0 && (
              <tr className="empty-row">
                <td colSpan={7}>{t("empty")}</td>
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
                        {d.size}
                        {d.pages > 0 && <> · {d.pages} {d.pages > 1 ? "pages" : "page"}</>}
                      </div>
                    </span>
                  </div>
                </td>
                <td className="mono-cell">{d.id.slice(0, 8)}</td>
                <td className="mono-cell">{d.type === "pdf" ? t("typePdf") : t("typeImage")}</td>
                <td className="mono-cell">{d.model ?? "—"}</td>
                <td className="mono-cell">{d.date}</td>
                <td>
                  {d.status === "proc" && d.progress != null ? (
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <Pill status="proc" />
                      <div className="mini-prog">
                        <i style={{ width: `${d.progress}%` }} />
                      </div>
                    </div>
                  ) : (
                    <Pill status={d.status} />
                  )}
                </td>
                <td>
                  <div className="row-actions" style={{ justifyContent: "flex-end" }}>
                    <button
                      className="dl"
                      title={t("download")}
                      aria-label={t("download")}
                      disabled={d.status !== "done" || busyId === d.id}
                      onClick={() => void download(d)}
                    >
                      <Download size={15} />
                    </button>
                    <button
                      title={t("view")}
                      aria-label={t("view")}
                      disabled={d.status !== "done" || busyId === d.id}
                      onClick={() => void viewResult(d)}
                    >
                      <Eye size={15} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="table-foot">
          <span>{t("showing", { shown: filtered.length, total: docs.length })}</span>
        </div>
      </div>

      {preview && (
        <PreviewModal
          title={preview.name}
          columns={preview.columns}
          rows={preview.rows}
          markdownUrl={preview.markdownUrl}
          loading={preview.loading}
          error={preview.error}
          onClose={() => setPreview(null)}
        />
      )}
    </div>
  );
}
