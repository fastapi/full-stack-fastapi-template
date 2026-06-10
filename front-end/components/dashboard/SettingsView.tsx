"use client";

import { useState } from "react";
import { Check, Copy, FileCheck2, FileSpreadsheet, FileText, RefreshCw } from "lucide-react";
import { useTranslations } from "next-intl";
import Toggle from "@/components/ui/Toggle";

type OptKey = "autoTables" | "mergePages" | "headers" | "ocr" | "notify";

const API_KEY = "txk_live_9f4Ad2QyR7sB1nMzKp83XwLcVeH0tGqJ";

export default function SettingsView() {
  const t = useTranslations("settings");
  const [opts, setOpts] = useState<Record<OptKey, boolean>>({
    autoTables: true,
    mergePages: true,
    headers: true,
    ocr: false,
    notify: true,
  });
  const [fmt, setFmt] = useState<"xlsx" | "csv">("xlsx");
  const [copied, setCopied] = useState(false);
  const flip = (k: OptKey) => setOpts((p) => ({ ...p, [k]: !p[k] }));

  const copy = () => {
    navigator.clipboard?.writeText(API_KEY).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 1600);
  };

  const toggles: { key: OptKey; t: string; d: string }[] = [
    { key: "autoTables", t: t("autoTablesT"), d: t("autoTablesD") },
    { key: "mergePages", t: t("mergePagesT"), d: t("mergePagesD") },
    { key: "headers", t: t("headersT"), d: t("headersD") },
    { key: "ocr", t: t("ocrT"), d: t("ocrD") },
    { key: "notify", t: t("notifyT"), d: t("notifyD") },
  ];

  return (
    <div className="settings-wrap">
      <div className="set-panel">
        <div className="sp-head">
          <h3>{t("parsingTitle")}</h3>
          <p>{t("parsingSub")}</p>
        </div>
        {toggles.map((row) => (
          <div className="set-row" key={row.key}>
            <div className="label">
              <div className="t">{row.t}</div>
              <div className="d">{row.d}</div>
            </div>
            <Toggle on={opts[row.key]} onToggle={() => flip(row.key)} label={row.t} />
          </div>
        ))}
      </div>

      <div className="set-panel">
        <div className="sp-head">
          <h3>{t("formatTitle")}</h3>
          <p>{t("formatSub")}</p>
        </div>
        <div style={{ padding: "18px 22px" }}>
          <div className="fmt-select">
            <div className={`fmt-opt ${fmt === "xlsx" ? "on" : ""}`} onClick={() => setFmt("xlsx")}>
              <span className="fo-ico">
                <FileSpreadsheet size={18} />
              </span>
              <span>
                <div className="fo-t">{t("xlsxT")}</div>
                <div className="fo-d">{t("xlsxD")}</div>
              </span>
              <span className="fo-check">
                <Check size={18} />
              </span>
            </div>
            <div className={`fmt-opt ${fmt === "csv" ? "on" : ""}`} onClick={() => setFmt("csv")}>
              <span className="fo-ico">
                <FileText size={18} />
              </span>
              <span>
                <div className="fo-t">{t("csvT")}</div>
                <div className="fo-d">{t("csvD")}</div>
              </span>
              <span className="fo-check">
                <Check size={18} />
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="set-panel">
        <div className="sp-head">
          <h3>{t("apiTitle")}</h3>
          <p>{t("apiSub")}</p>
        </div>
        <div className="api-row">
          <div className="api-field">
            <div className="api-key">
              <FileCheck2 size={15} style={{ color: "var(--cyan)", flex: "none" }} />
              <span className="k">{API_KEY}</span>
            </div>
            <button className={`btn btn-ghost copy-btn ${copied ? "copied" : ""}`} onClick={copy}>
              {copied ? (
                <>
                  <Check size={15} /> {t("copied")}
                </>
              ) : (
                <>
                  <Copy size={15} /> {t("copy")}
                </>
              )}
            </button>
            <button className="btn btn-ghost" title={t("regenerate")} aria-label={t("regenerate")}>
              <RefreshCw size={15} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
