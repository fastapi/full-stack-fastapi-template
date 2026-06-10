"use client";

import { useTranslations } from "next-intl";
import type { DocStatus } from "@/lib/data";

export interface PillProps {
  status: DocStatus;
}

export default function Pill({ status }: PillProps) {
  const t = useTranslations("status");
  return (
    <span className={`pill ${status}`}>
      <span className="dot" />
      {t(status)}
    </span>
  );
}
