"use client";

import { useState, type ReactNode } from "react";
import { Building2, FileSpreadsheet, LayoutDashboard, Menu, Settings, Users, X, type LucideIcon } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link, usePathname } from "@/lib/navigation";
import ThemeToggle from "@/components/ui/ThemeToggle";
import LocaleSwitcher from "@/components/ui/LocaleSwitcher";
import LogoutButton from "@/components/ui/LogoutButton";
import Badge from "@/components/ui/Badge";
import type { AuthUser } from "@/lib/auth";

interface AdminNavItem {
  key: string;
  href: string;
  titleKey: string;
  Icon: LucideIcon;
}

const NAV: AdminNavItem[] = [
  { key: "dashboard", href: "/dashboard", titleKey: "overview", Icon: LayoutDashboard },
  { key: "users", href: "/users", titleKey: "users", Icon: Users },
  { key: "companies", href: "/companies", titleKey: "companies", Icon: Building2 },
  { key: "settings", href: "/settings", titleKey: "settings", Icon: Settings },
];

export default function AdminShell({ user, children }: { user: AuthUser; children: ReactNode }) {
  const t = useTranslations();
  const tShell = useTranslations("shell");
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const active = NAV.find((n) => pathname === n.href || pathname.startsWith(n.href + "/")) ?? NAV[0];

  return (
    <div className="admin-shell">
      <header className="admin-top">
        <div className="brand">
          <span className="glyph">
            <FileSpreadsheet size={16} strokeWidth={2.4} />
          </span>
          <span className="wordmark">TABULA</span>
        </div>

        <nav className={`admin-nav ${open ? "open" : ""}`}>
          {NAV.map((n) => (
            <Link
              key={n.key}
              href={n.href}
              className={active.key === n.key ? "active" : ""}
              onClick={() => setOpen(false)}
            >
              <n.Icon size={15} />
              {t(`shell.nav.${n.key}`)}
            </Link>
          ))}
        </nav>

        <div className="admin-spacer" />
        <ThemeToggle />
        <LocaleSwitcher />
        <div className="topbar-user">
          <Badge tone="bad">{tShell("roleAdmin")}</Badge>
          <span className="topbar-avatar">{user.initials}</span>
        </div>
        <LogoutButton />
        <button
          className="icon-btn admin-burger"
          onClick={() => setOpen((o) => !o)}
          aria-label={t("common.menu")}
        >
          {open ? <X size={18} /> : <Menu size={18} />}
        </button>
      </header>

      <main className="admin-content">
        <div className="block-head">
          <div>
            <h1 style={{ fontFamily: "var(--font-display)", fontSize: 22, fontWeight: 600, margin: 0 }}>
              {t(`pages.${active.titleKey}.title`)}
            </h1>
            <div className="crumb" style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--fg-dim)", marginTop: 4 }}>
              {t(`pages.${active.titleKey}.sub`)}
            </div>
          </div>
        </div>
        {children}
      </main>
    </div>
  );
}
