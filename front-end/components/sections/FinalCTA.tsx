"use client";

import { ArrowRight, Play } from "lucide-react";
import { useTranslations } from "next-intl";
import Reveal from "@/components/sections/Reveal";
import { Link } from "@/lib/navigation";

export default function FinalCTA() {
  const t = useTranslations("landing.cta");
  const tHero = useTranslations("landing.hero");
  return (
    <section className="final-cta">
      <Reveal>
        <h2>
          {t("title1")}
          <br />
          <span className="serif">{t("title2")}</span>
        </h2>
        <p>{t("body")}</p>
        <div className="hero-cta" style={{ marginTop: 0 }}>
          <Link href="/signup" className="btn btn-primary">
            {tHero("startFree")} <ArrowRight size={16} />
          </Link>
          <Link href="/login" className="btn btn-ghost">
            <Play size={15} /> {tHero("seeDemo")}
          </Link>
        </div>
      </Reveal>
    </section>
  );
}
