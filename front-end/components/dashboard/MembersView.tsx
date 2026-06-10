"use client";

import { MoreHorizontal } from "lucide-react";
import { useTranslations } from "next-intl";
import { MEMBERS } from "@/lib/data";

export default function MembersView() {
  const t = useTranslations("members");
  const tRoles = useTranslations("roles");

  return (
    <div className="table-wrap">
      <table className="tbl">
        <thead>
          <tr>
            <th>{t("colMember")}</th>
            <th>{t("colRole")}</th>
            <th>{t("colJobs")}</th>
            <th style={{ textAlign: "right" }}>{t("colActions")}</th>
          </tr>
        </thead>
        <tbody>
          {MEMBERS.map((u) => (
            <tr key={u.email}>
              <td>
                <div className="fname">
                  <span className="users-avatar" style={{ background: u.gradient }}>
                    {u.name
                      .split(" ")
                      .map((x) => x[0])
                      .join("")}
                  </span>
                  <span>
                    <div className="nm">{u.name}</div>
                    <div className="sz">{u.email}</div>
                  </span>
                </div>
              </td>
              <td className="mono-cell">{tRoles(u.roleKey)}</td>
              <td className="mono-cell">{u.jobs.toLocaleString()}</td>
              <td>
                <div className="row-actions" style={{ justifyContent: "flex-end" }}>
                  <button aria-label={t("colActions")}>
                    <MoreHorizontal size={15} />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="table-foot">
        <span>{t("footCount", { count: MEMBERS.length })}</span>
        <span>{t("seats", { count: MEMBERS.length })}</span>
      </div>
    </div>
  );
}
