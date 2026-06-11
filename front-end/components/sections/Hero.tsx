"use client";

import { useEffect, useState } from "react";
import { ArrowRight, CheckCircle2, FileSpreadsheet, FileText, Play, Sparkles } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link } from "@/lib/navigation";

function Typewriter() {
  const t = useTranslations("landing.hero");
  const segments = [
    { text: t("headStart"), cls: "" },
    { text: t("headData"), cls: "cy" },
    { text: t("headDash"), cls: "" },
    { text: t("headInstantly"), cls: "am" },
  ];
  const total = segments.reduce((a, s) => a + s.text.length, 0);
  const [count, setCount] = useState(0);

  useEffect(() => {
    let i = 0;
    const id = setInterval(() => {
      i += 1;
      setCount(i);
      if (i >= total) clearInterval(id);
    }, 52);
    return () => clearInterval(id);
  }, [total]);

  let remaining = count;
  const done = count >= total;
  return (
    <h1 className="hero-h1">
      {segments.map((seg, idx) => {
        const take = Math.max(0, Math.min(seg.text.length, remaining));
        remaining -= seg.text.length;
        return (
          <span key={idx} className={seg.cls}>
            {seg.text.slice(0, take)}
          </span>
        );
      })}
      <span className="cursor" style={{ opacity: done ? undefined : 1 }} />
    </h1>
  );
}

function HeroPreview() {
  const t = useTranslations("landing.preview");
  const cols = ["INVOICE #", "DATE", "VENDOR", "AMOUNT"];
  const rows = [
    ["INV-2041", "06 / 02", "Northwind Co.", "$ 12,480.00"],
    ["INV-2042", "06 / 03", "Acme Freight", "$  4,215.50"],
    ["INV-2043", "06 / 05", "Globex Ltd.", "$ 28,900.00"],
    ["INV-2044", "06 / 06", "Initech LLC", "$  1,099.99"],
  ];
  return (
    <div className="hero-preview" id="preview">
      <div className="preview-frame">
        <div className="preview-bar">
          <span className="dot" />
          <span className="dot" />
          <span className="dot" />
          <span className="addr">{t("addr")}</span>
        </div>
        <div className="preview-body">
          <div className="preview-col scan">
            <div className="pv-label">
              <FileText size={13} /> {t("source")}
            </div>
            {[92, 70, 84, 60, 78, 88, 64, 74, 56].map((w, i) => (
              <div key={i} className="pv-doc-line" style={{ width: `${w}%`, opacity: 1 - i * 0.06 }} />
            ))}
          </div>
          <div className="preview-col">
            <div className="pv-label">
              <FileSpreadsheet size={13} /> {t("extracted")}
            </div>
            <div className="pv-grid">
              {cols.map((c) => (
                <div key={c} className="pv-cell head">
                  {c}
                </div>
              ))}
              {rows.map((r, ri) =>
                r.map((cell, ci) => (
                  <div key={ri + "-" + ci} className={`pv-cell ${ci === 3 ? "num" : ""}`}>
                    {cell}
                  </div>
                )),
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Hero() {
  const t = useTranslations("landing.hero");
  return (
    <>
      <header className="hero">
        <span className="hero-badge">
          <span className="spark">
            <Sparkles size={14} />
          </span>
          {t("badge")}
          <b>{t("badgeStrong")}</b>
        </span>
        <Typewriter />
        <p className="hero-sub">
          {t.rich("sub", {
            excel: (chunks) => <span className="serif">{chunks}</span>,
          })}
        </p>
        <div className="hero-cta">
          <Link href="/signup" className="btn btn-primary">
            {t("startFree")} <ArrowRight size={16} />
          </Link>
          <Link href="/login" className="btn btn-ghost">
            <Play size={15} /> {t("seeDemo")}
          </Link>
        </div>
        <div className="hero-proof">
          <span>
            <CheckCircle2 className="ok" size={14} /> {t("proofNoCard")}
          </span>
          <span>
            <CheckCircle2 className="ok" size={14} /> {t("proofFreePages")}
          </span>
          <span>
            <CheckCircle2 className="ok" size={14} /> {t("proofSoc2")}
          </span>
        </div>
      </header>
      <HeroPreview />
    </>
  );
}
