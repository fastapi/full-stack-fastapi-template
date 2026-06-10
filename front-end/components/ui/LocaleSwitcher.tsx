"use client";

import { useState, useTransition } from "react";
import { useLocale, useTranslations } from "next-intl";
import { Check, Globe } from "lucide-react";
import { usePathname, useRouter } from "@/lib/navigation";
import { locales, localeNames, type Locale } from "@/lib/i18n";

export default function LocaleSwitcher() {
  const t = useTranslations("common");
  const active = useLocale() as Locale;
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [isPending, startTransition] = useTransition();

  const select = (locale: Locale) => {
    setOpen(false);
    if (locale === active) return;
    startTransition(() => {
      router.replace(pathname, { locale });
    });
  };

  return (
    <div className="relative">
      <button
        type="button"
        className="icon-btn"
        aria-label={t("language")}
        aria-haspopup="listbox"
        aria-expanded={open}
        disabled={isPending}
        onClick={() => setOpen((o) => !o)}
      >
        <Globe size={17} />
      </button>

      {open && (
        <>
          <button
            className="fixed inset-0 z-40 cursor-default"
            aria-hidden="true"
            tabIndex={-1}
            onClick={() => setOpen(false)}
          />
          <ul
            role="listbox"
            className="absolute right-0 z-50 mt-2 min-w-[160px] overflow-hidden rounded border border-line bg-surface-2 py-1 font-mono text-[13px] shadow-panel"
          >
            {locales.map((locale) => (
              <li key={locale}>
                <button
                  type="button"
                  role="option"
                  aria-selected={locale === active}
                  className="flex w-full items-center justify-between gap-3 px-3 py-2 text-left text-fg-muted transition-colors hover:bg-[var(--wash-04)] hover:text-fg"
                  onClick={() => select(locale)}
                >
                  {localeNames[locale]}
                  {locale === active && <Check size={14} className="text-cyan" />}
                </button>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
