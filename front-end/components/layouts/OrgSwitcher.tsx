"use client";

import { useState } from "react";
import { Check, ChevronsUpDown } from "lucide-react";
import { useTranslations } from "next-intl";

export interface OrgSwitcherProps {
  companyName: string;
}

const OTHER_ORGS = ["Acme Freight", "Globex Ltd."];

export default function OrgSwitcher({ companyName }: OrgSwitcherProps) {
  const t = useTranslations("shell");
  const [open, setOpen] = useState(false);
  const initials = companyName
    .split(" ")
    .map((w) => w[0])
    .join("")
    .slice(0, 2);

  return (
    <div className="org-switch">
      <button
        className="org-btn"
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={t("switchOrg")}
        onClick={() => setOpen((o) => !o)}
      >
        <span className="org-logo">{initials}</span>
        <span className="org-name">{companyName}</span>
        <ChevronsUpDown size={14} className="org-chev" />
      </button>
      {open && (
        <div className="org-menu" role="menu">
          <button role="menuitem" onClick={() => setOpen(false)}>
            <Check size={14} style={{ color: "var(--cyan)" }} />
            {companyName}
          </button>
          {OTHER_ORGS.map((org) => (
            <button key={org} role="menuitem" onClick={() => setOpen(false)}>
              <span style={{ width: 14, display: "inline-block" }} />
              {org}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
