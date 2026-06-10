"use client";

import { ArrowRight, Play } from "lucide-react";
import { useTranslations } from "next-intl";
import Reveal from "@/components/sections/Reveal";
import { LaunchButton } from "@/components/ui/RoleSwitcher";

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
          <LaunchButton variant="primary">
            {tHero("startFree")} <ArrowRight size={16} />
          </LaunchButton>
          <LaunchButton variant="ghost">
            <Play size={15} /> {tHero("seeDemo")}
          </LaunchButton>
        </div>
      </Reveal>
    </section>
  );
}
