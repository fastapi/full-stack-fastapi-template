"use client";

import type { ReactNode } from "react";
import { CreditCard, LayoutDashboard, Settings, Users } from "lucide-react";
import SidebarShell, { type NavItem } from "@/components/layouts/SidebarShell";
import OrgSwitcher from "@/components/layouts/OrgSwitcher";
import type { AuthUser } from "@/lib/auth";

const NAV: NavItem[] = [
  { key: "dashboard", href: "/dashboard", titleKey: "overview", Icon: LayoutDashboard },
  { key: "members", href: "/members", titleKey: "members", Icon: Users },
  { key: "billing", href: "/billing", titleKey: "billing", Icon: CreditCard },
  { key: "settings", href: "/settings", titleKey: "settings", Icon: Settings },
];

export default function CompanyShell({ user, children }: { user: AuthUser; children: ReactNode }) {
  return (
    <SidebarShell
      user={user}
      accent="amber"
      nav={NAV}
      roleBadgeTone="amber"
      roleBadgeKey="roleCompany"
      orgSwitcher={<OrgSwitcher companyName={user.companyName ?? "Northwind Co."} />}
    >
      {children}
    </SidebarShell>
  );
}
