"use client";

import { useState, useTransition } from "react";
import { useLocale, useTranslations } from "next-intl";
import { ArrowUpRight, Building2, ShieldCheck, User } from "lucide-react";
import { launchAs } from "@/lib/actions";
import type { UserRole } from "@/lib/auth";
import { cn } from "@/lib/utils";

const ROLE_META: { role: UserRole; key: "user" | "company" | "admin"; icon: typeof User }[] = [
  { role: "user", key: "user", icon: User },
  { role: "company", key: "company", icon: Building2 },
  { role: "admin", key: "admin", icon: ShieldCheck },
];

/** "Launch App" trigger that opens a menu to enter any of the three role shells. */
export default function RoleSwitcher({ className }: { className?: string }) {
  const t = useTranslations("landing.launch");
  const locale = useLocale();
  const [open, setOpen] = useState(false);
  const [isPending, startTransition] = useTransition();

  const go = (role: UserRole) => {
    setOpen(false);
    startTransition(() => {
      void launchAs(locale, role);
    });
  };

  const tNav = useTranslations("landing.nav");

  return (
    <div className={cn("relative", className)}>
      <button
        type="button"
        className="btn btn-ghost"
        aria-haspopup="menu"
        aria-expanded={open}
        disabled={isPending}
        onClick={() => setOpen((o) => !o)}
      >
        {tNav("launch")} <ArrowUpRight size={15} />
      </button>

      {open && (
        <>
          <button
            className="fixed inset-0 z-40 cursor-default"
            aria-hidden="true"
            tabIndex={-1}
            onClick={() => setOpen(false)}
          />
          <div
            role="menu"
            className="absolute right-0 z-50 mt-2 w-[230px] overflow-hidden rounded-lg border border-line bg-surface-2 p-1.5 shadow-panel"
          >
            <div className="px-2.5 py-1.5 font-mono text-[10px] uppercase tracking-[0.16em] text-fg-faint">
              {t("label")}
            </div>
            {ROLE_META.map(({ role, key, icon: Icon }) => (
              <button
                key={role}
                type="button"
                role="menuitem"
                className="flex w-full items-center gap-3 rounded px-2.5 py-2 text-left transition-colors hover:bg-[var(--wash-04)]"
                onClick={() => go(role)}
              >
                <span className="grid h-8 w-8 place-items-center rounded-md border border-line text-cyan">
                  <Icon size={16} />
                </span>
                <span className="font-mono text-[13px] text-fg">{t(key)}</span>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

/** Primary/ghost CTA that launches directly into a given role (default user). */
export function LaunchButton({
  variant = "primary",
  role = "user",
  className,
  children,
}: {
  variant?: "primary" | "ghost";
  role?: UserRole;
  className?: string;
  children: React.ReactNode;
}) {
  const locale = useLocale();
  const [isPending, startTransition] = useTransition();
  return (
    <button
      type="button"
      className={cn("btn", variant === "primary" ? "btn-primary" : "btn-ghost", className)}
      disabled={isPending}
      onClick={() => startTransition(() => void launchAs(locale, role))}
    >
      {children}
    </button>
  );
}
