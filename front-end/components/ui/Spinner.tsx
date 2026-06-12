"use client";

import { Loader2 } from "lucide-react";
import { useTranslations } from "next-intl";

/** Centered page-level loading indicator shown while a route segment loads. */
export default function Spinner() {
  const t = useTranslations("common");
  return (
    <div className="page-loading" role="status" aria-live="polite">
      <Loader2 size={28} className="spin" aria-hidden />
      <span>{t("loading")}</span>
    </div>
  );
}
