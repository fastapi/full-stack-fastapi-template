"use client";

import { useTransition } from "react";
import { useLocale, useTranslations } from "next-intl";
import { LogOut } from "lucide-react";
import { logout } from "@/lib/actions";

export default function LogoutButton() {
  const t = useTranslations("common");
  const locale = useLocale();
  const [isPending, startTransition] = useTransition();

  return (
    <button
      type="button"
      className="icon-btn"
      title={t("logout")}
      aria-label={t("logout")}
      disabled={isPending}
      onClick={() => startTransition(() => void logout(locale))}
    >
      <LogOut size={17} />
    </button>
  );
}
