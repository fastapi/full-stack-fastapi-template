"use client";

import { useTranslations } from "next-intl";
import ActivityFeed from "@/components/dashboard/ActivityFeed";
import type { AuthUser } from "@/lib/auth";
import { DOCS } from "@/lib/data";

const ROLE_LABEL: Record<AuthUser["role"], "roleUser" | "roleCompany" | "roleAdmin"> = {
  user: "roleUser",
  company: "roleCompany",
  admin: "roleAdmin",
};

export interface ProfileViewProps {
  user: AuthUser;
}

export default function ProfileView({ user }: ProfileViewProps) {
  const t = useTranslations("profile");
  const tShell = useTranslations("shell");

  const rows: { label: string; value: string }[] = [
    { label: t("fieldName"), value: user.name },
    { label: t("fieldEmail"), value: user.email },
    { label: t("fieldRole"), value: tShell(ROLE_LABEL[user.role]) },
    { label: t("fieldPlan"), value: user.plan },
  ];

  return (
    <div className="settings-wrap">
      <div className="set-panel">
        <div className="sp-head" style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <span className="sb-avatar" style={{ width: 44, height: 44, fontSize: 15 }}>
            {user.initials}
          </span>
          <div>
            <h3>{t("detailsTitle")}</h3>
            <p>{t("detailsSub")}</p>
          </div>
        </div>
        {rows.map((r) => (
          <div className="set-row" key={r.label}>
            <div className="label">
              <div className="d" style={{ marginTop: 0 }}>
                {r.label}
              </div>
            </div>
            <div className="t" style={{ fontFamily: "var(--font-mono)", fontSize: 13.5 }}>
              {r.value}
            </div>
          </div>
        ))}
        <div className="set-row">
          <div className="label" />
          <button className="btn btn-primary">{t("edit")}</button>
        </div>
      </div>

      <div className="panel">
        <div className="panel-head">
          <div>
            <h3>{t("recentTitle")}</h3>
            <div className="sub">{t("recentSub")}</div>
          </div>
        </div>
        <ActivityFeed items={DOCS.slice(0, 5)} />
      </div>
    </div>
  );
}
