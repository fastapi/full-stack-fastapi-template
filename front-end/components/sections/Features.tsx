"use client";

import type { ReactNode } from "react";
import { Code2, Files, FileSpreadsheet, Layers, Table, Zap } from "lucide-react";
import { useTranslations } from "next-intl";
import Reveal from "@/components/sections/Reveal";

interface FeatureDef {
  ico: ReactNode;
  titleKey: string;
  descKey: string;
  tags: string[];
}

const FEATURES: FeatureDef[] = [
  { ico: <Files size={20} />, titleKey: "f1Title", descKey: "f1Desc", tags: ["PDF", "JPG", "PNG", "TIFF"] },
  { ico: <Layers size={20} />, titleKey: "f2Title", descKey: "f2Desc", tags: ["Parallel", "Queues", "Webhooks"] },
  { ico: <Table size={20} />, titleKey: "f3Title", descKey: "f3Desc", tags: ["Auto-headers", "Cell merge"] },
  { ico: <FileSpreadsheet size={20} />, titleKey: "f4Title", descKey: "f4Desc", tags: ["XLSX", "CSV", "Typed cols"] },
  { ico: <Code2 size={20} />, titleKey: "f5Title", descKey: "f5Desc", tags: ["REST", "Python", "Node"] },
  { ico: <Zap size={20} />, titleKey: "f6Title", descKey: "f6Desc", tags: ["GPU", "Realtime"] },
];

function Feature({ f, delay }: { f: FeatureDef; delay: number }) {
  const t = useTranslations("landing.features");
  const onMove: React.MouseEventHandler<HTMLDivElement> = (e) => {
    const r = e.currentTarget.getBoundingClientRect();
    e.currentTarget.style.setProperty("--mx", `${e.clientX - r.left}px`);
    e.currentTarget.style.setProperty("--my", `${e.clientY - r.top}px`);
  };
  return (
    <Reveal delay={delay} className="feature" onMouseMove={onMove}>
      <div className="f-ico">{f.ico}</div>
      <h3>{t(f.titleKey)}</h3>
      <p>{t(f.descKey)}</p>
      <div className="f-tags">
        {f.tags.map((tag) => (
          <span key={tag} className="f-chip">
            {tag}
          </span>
        ))}
      </div>
    </Reveal>
  );
}

export default function Features() {
  const t = useTranslations("landing.features");
  return (
    <section className="section" id="features">
      <Reveal className="section-kicker">{t("kicker")}</Reveal>
      <Reveal delay={60}>
        <h2 className="section-title">
          {t("titlePre")}
          <span className="serif">{t("titleEm")}</span>
          {t("titlePost")}
        </h2>
        <p className="section-lead">{t("lead")}</p>
      </Reveal>
      <div className="features">
        {FEATURES.map((f, i) => (
          <Feature key={f.titleKey} f={f} delay={(i % 3) * 110} />
        ))}
      </div>
    </section>
  );
}
