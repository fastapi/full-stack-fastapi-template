"use client";

import type { ReactNode } from "react";
import { ArrowRight, Download, ScanLine, Upload } from "lucide-react";
import { useTranslations } from "next-intl";
import Reveal from "@/components/sections/Reveal";

interface Step {
  n: string;
  ico: ReactNode;
  am: boolean;
  titleKey: "s1Title" | "s2Title" | "s3Title";
  descKey: "s1Desc" | "s2Desc" | "s3Desc";
}

const STEPS: Step[] = [
  { n: "01", ico: <Upload size={22} />, am: false, titleKey: "s1Title", descKey: "s1Desc" },
  { n: "02", ico: <ScanLine size={22} />, am: true, titleKey: "s2Title", descKey: "s2Desc" },
  { n: "03", ico: <Download size={22} />, am: false, titleKey: "s3Title", descKey: "s3Desc" },
];

export default function HowItWorks() {
  const t = useTranslations("landing.how");
  return (
    <section className="section" id="how">
      <Reveal className="section-kicker">{t("kicker")}</Reveal>
      <Reveal delay={60}>
        <h2 className="section-title">
          {t("titlePre")}
          <span className="serif">{t("titleEm")}</span>
          {t("titlePost")}
        </h2>
        <p className="section-lead">{t("lead")}</p>
      </Reveal>
      <div className="steps">
        {STEPS.map((s, i) => (
          <Reveal key={s.n} delay={i * 130} className="step">
            <div className="step-num">
              {t("step")} / {s.n}
            </div>
            <div className={`step-ico ${s.am ? "am" : ""}`}>{s.ico}</div>
            <h3>{t(s.titleKey)}</h3>
            <p>{t(s.descKey)}</p>
            <span className="step-arrow">
              <ArrowRight size={20} />
            </span>
          </Reveal>
        ))}
      </div>
    </section>
  );
}
