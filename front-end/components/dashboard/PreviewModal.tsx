"use client";

import { useEffect } from "react";
import { ExternalLink, X } from "lucide-react";
import { useTranslations } from "next-intl";

type PreviewRow = Record<string, unknown>;

interface PreviewModalProps {
  title: string;
  columns: string[];
  rows: PreviewRow[];
  markdownUrl: string | null;
  loading: boolean;
  error: string | null;
  onClose: () => void;
}

// Add comma thousands separators to a numeric string while keeping the dot
// decimal and any sign. Operates on the string so large integers (e.g. IDs)
// don't lose precision through Number().
function groupNumberString(numeric: string): string {
  const match = /^(-?)(\d+)(\.\d+)?$/.exec(numeric);
  if (!match) return numeric;
  const [, sign, intPart, decPart = ""] = match;
  const grouped = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return `${sign}${grouped}${decPart}`;
}

function formatCell(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "number") {
    return Number.isFinite(value)
      ? groupNumberString(String(value))
      : String(value);
  }
  if (typeof value === "object") return JSON.stringify(value);

  const str = String(value);
  // If the text is a number only, render it with comma/dot grouping.
  const trimmed = str.trim();
  if (/^-?\d+(\.\d+)?$/.test(trimmed)) {
    return groupNumberString(trimmed);
  }
  return str;
}

export default function PreviewModal({
  title,
  columns,
  rows,
  markdownUrl,
  loading,
  error,
  onClose,
}: PreviewModalProps) {
  const t = useTranslations("documents");
  const tc = useTranslations("common");

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const isEmpty = columns.length === 0 || rows.length === 0;

  return (
    <div className="modal-overlay" onClick={onClose} role="presentation">
      <div
        className="modal preview-modal"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={t("previewTitle")}
      >
        <div className="modal-head">
          <div>
            <div className="modal-title">{t("previewTitle")}</div>
            <div className="modal-sub">{title}</div>
          </div>
          <button className="modal-close" onClick={onClose} aria-label={tc("close")}>
            <X size={16} />
          </button>
        </div>

        <div className="modal-body preview-body-scroll">
          {loading && <div className="preview-state">{tc("loading")}</div>}
          {!loading && error && <div className="preview-state field-error">{error}</div>}
          {!loading && !error && isEmpty && (
            <div className="preview-state">{t("previewEmpty")}</div>
          )}
          {!loading && !error && !isEmpty && (
            <div className="preview-table">
              <table className="tbl">
                <thead>
                  <tr>
                    {columns.map((col) => (
                      <th key={col}>{col}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, i) => (
                    <tr key={i}>
                      {columns.map((col) => (
                        <td key={col}>{formatCell(row[col])}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {markdownUrl && (
          <div className="modal-foot">
            <a
              className="ghost-link"
              href={markdownUrl}
              target="_blank"
              rel="noopener noreferrer"
            >
              <ExternalLink size={13} /> {t("previewOpenRaw")}
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
