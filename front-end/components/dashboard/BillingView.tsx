"use client";

import { Download } from "lucide-react";
import { useTranslations } from "next-intl";

const INVOICES = [
  { id: "INV-2026-06", date: "2026-06-01", amount: "$240.00" },
  { id: "INV-2026-05", date: "2026-05-01", amount: "$240.00" },
  { id: "INV-2026-04", date: "2026-04-01", amount: "$240.00" },
  { id: "INV-2026-03", date: "2026-03-01", amount: "$180.00" },
];

const USAGE_PCT = 62;

export default function BillingView() {
  const t = useTranslations("billing");

  return (
    <div className="settings-wrap">
      <div className="set-panel">
        <div className="sp-head">
          <h3>{t("planTitle")}</h3>
          <p>{t("planSub")}</p>
        </div>
        <div className="set-row">
          <div className="label">
            <div className="t" style={{ fontFamily: "var(--font-mono)", color: "var(--cyan)" }}>
              {t("planName")}
            </div>
            <div className="d">{t("planAllowance")}</div>
          </div>
          <button className="btn btn-ghost">{t("managePlan")}</button>
        </div>
      </div>

      <div className="set-panel">
        <div className="sp-head">
          <h3>{t("usageTitle")}</h3>
          <p>{t("usageSub")}</p>
        </div>
        <div style={{ padding: "18px 22px" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              fontFamily: "var(--font-mono)",
              fontSize: 12,
              color: "var(--fg-dim)",
              marginBottom: 10,
            }}
          >
            <span>{t("usageLabel")}</span>
            <span>{t("usageValue")}</span>
          </div>
          <div className="fq-bar" style={{ height: 8 }}>
            <i style={{ width: `${USAGE_PCT}%`, background: "var(--cyan)" }} />
          </div>
        </div>
      </div>

      <div className="set-panel">
        <div className="sp-head">
          <h3>{t("invoicesTitle")}</h3>
          <p>{t("invoicesSub")}</p>
        </div>
        <table className="tbl">
          <thead>
            <tr>
              <th>{t("colInvoice")}</th>
              <th>{t("colDate")}</th>
              <th>{t("colAmount")}</th>
              <th>{t("colStatus")}</th>
              <th style={{ textAlign: "right" }}>{t("download")}</th>
            </tr>
          </thead>
          <tbody>
            {INVOICES.map((inv) => (
              <tr key={inv.id}>
                <td className="mono-cell">{inv.id}</td>
                <td className="mono-cell">{inv.date}</td>
                <td className="mono-cell">{inv.amount}</td>
                <td>
                  <span className="pill done">
                    <span className="dot" />
                    {t("paid")}
                  </span>
                </td>
                <td>
                  <div className="row-actions" style={{ justifyContent: "flex-end" }}>
                    <button className="dl" aria-label={t("download")} title={t("download")}>
                      <Download size={15} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
