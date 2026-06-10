"use client";

import { useEffect, useState } from "react";
import { FileSpreadsheet } from "lucide-react";
import { useTranslations } from "next-intl";
import RoleSwitcher from "@/components/ui/RoleSwitcher";

function useScrolled(threshold = 12) {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > threshold);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [threshold]);
  return scrolled;
}

export default function Nav() {
  const t = useTranslations("landing.nav");
  const scrolled = useScrolled();
  return (
    <nav className={`lp-nav ${scrolled ? "scrolled" : ""}`}>
      <div className="brand">
        <span className="glyph">
          <FileSpreadsheet size={16} strokeWidth={2.4} />
        </span>
        <span className="wordmark">TABULA</span>
      </div>
      <div className="lp-nav-links">
        <a href="#how">{t("how")}</a>
        <a href="#features">{t("features")}</a>
        <a href="#stats">{t("accuracy")}</a>
      </div>
      <div className="lp-nav-cta">
        <RoleSwitcher />
      </div>
    </nav>
  );
}
