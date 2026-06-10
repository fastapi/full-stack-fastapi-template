"use client";

import type { ReactNode } from "react";
import { FileText, LayoutDashboard, Settings, UploadCloud, User } from "lucide-react";
import SidebarShell, { type NavItem } from "@/components/layouts/SidebarShell";
import type { AuthUser } from "@/lib/auth";
import { DOCS } from "@/lib/data";

const NAV: NavItem[] = [
  { key: "dashboard", href: "/dashboard", titleKey: "overview", Icon: LayoutDashboard },
  { key: "documents", href: "/documents", titleKey: "documents", Icon: FileText, count: DOCS.length },
  { key: "upload", href: "/upload", titleKey: "upload", Icon: UploadCloud },
  { key: "profile", href: "/profile", titleKey: "profile", Icon: User },
  { key: "settings", href: "/settings", titleKey: "settings", Icon: Settings },
];

export default function UserShell({ user, children }: { user: AuthUser; children: ReactNode }) {
  return (
    <SidebarShell user={user} accent="cyan" nav={NAV} roleBadgeTone="cyan" roleBadgeKey="roleUser">
      {children}
    </SidebarShell>
  );
}
