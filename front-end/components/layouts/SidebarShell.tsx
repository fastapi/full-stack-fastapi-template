"use client";

import { useState, type ReactNode } from "react";
import { Bell, Menu, PanelLeftClose, PanelLeftOpen, Search, FileSpreadsheet, type LucideIcon } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link, usePathname } from "@/lib/navigation";
import ThemeToggle from "@/components/ui/ThemeToggle";
import LocaleSwitcher from "@/components/ui/LocaleSwitcher";
import Badge from "@/components/ui/Badge";
import type { AuthUser } from "@/lib/auth";

export interface NavItem {
  key: string;
  href: string;
  titleKey: string;
  Icon: LucideIcon;
  count?: number;
}

export interface SidebarShellProps {
  user: AuthUser;
  accent: "cyan" | "amber";
  nav: NavItem[];
  roleBadgeTone: "cyan" | "amber" | "bad";
  roleBadgeKey: "roleUser" | "roleCompany" | "roleAdmin";
  orgSwitcher?: ReactNode;
  children: ReactNode;
}

export default function SidebarShell({
  user,
  accent,
  nav,
  roleBadgeTone,
  roleBadgeKey,
  orgSwitcher,
  children,
}: SidebarShellProps) {
  const t = useTranslations();
  const tShell = useTranslations("shell");
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const active =
    nav.find((n) => pathname === n.href || pathname.startsWith(n.href + "/")) ?? nav[0];

  return (
    <div
      className={`dash ${collapsed ? "collapsed" : ""} ${mobileOpen ? "mobile-open" : ""} ${
        accent === "amber" ? "accent-amber" : ""
      }`}
    >
      <aside className="sidebar">
        <div className="sb-head">
          <div className="sb-brand">
            <span className="glyph">
              <FileSpreadsheet size={16} strokeWidth={2.4} />
            </span>
            <span className="wm">TABULA</span>
          </div>
          <button
            className="sb-toggle"
            title={tShell("collapse")}
            aria-label={tShell("collapse")}
            onClick={() => setCollapsed((c) => !c)}
          >
            {collapsed ? <PanelLeftOpen size={16} /> : <PanelLeftClose size={16} />}
          </button>
        </div>

        {orgSwitcher}

        <div className="sb-section-label">{tShell("workspace")}</div>
        <nav className="sb-nav">
          {nav.map((n) => {
            const isActive = active.key === n.key;
            return (
              <Link
                key={n.key}
                href={n.href}
                className={`sb-item ${isActive ? "active" : ""}`}
                title={t(`shell.nav.${n.key}`)}
                onClick={() => setMobileOpen(false)}
              >
                <span className="ico">
                  <n.Icon size={18} />
                </span>
                <span className="lbl">{t(`shell.nav.${n.key}`)}</span>
                {n.count != null && <span className="count">{n.count}</span>}
              </Link>
            );
          })}
        </nav>

        <div className="sb-foot">
          <div className="sb-user">
            <span className="sb-avatar">{user.initials}</span>
            <span className="meta">
              <div className="n">{user.name}</div>
              <div className="e">{user.plan}</div>
            </span>
          </div>
        </div>
      </aside>

      <div className="sb-scrim" onClick={() => setMobileOpen(false)} />

      <div className="main">
        <header className="topbar">
          <button
            className="icon-btn hamburger"
            onClick={() => setMobileOpen(true)}
            title={t("common.menu")}
            aria-label={t("common.menu")}
          >
            <Menu size={18} />
          </button>
          <div>
            <h1>{t(`pages.${active.titleKey}.title`)}</h1>
            <div className="crumb">tabula / {active.key}</div>
          </div>
          <div className="topbar-spacer" />
          <div className="topbar-search">
            <Search size={15} />
            <input placeholder={tShell("searchPlaceholder")} aria-label={t("common.search")} />
          </div>
          <button className="icon-btn" title={t("common.notifications")} aria-label={t("common.notifications")}>
            <Bell size={17} />
            <span className="badge-dot" />
          </button>
          <ThemeToggle />
          <LocaleSwitcher />
          <div className="topbar-user">
            <Badge tone={roleBadgeTone}>{tShell(roleBadgeKey)}</Badge>
            <span className="topbar-avatar">{user.initials}</span>
          </div>
        </header>
        <div className="content">{children}</div>
      </div>
    </div>
  );
}
