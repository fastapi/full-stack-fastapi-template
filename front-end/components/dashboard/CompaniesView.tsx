"use client";

import { Building2, MoreHorizontal } from "lucide-react";
import { useTranslations } from "next-intl";
import Pill from "@/components/ui/Pill";
import { COMPANIES } from "@/lib/data";

export default function CompaniesView() {
  const t = useTranslations("companies");
  const tPlans = useTranslations("companies.plans");

  return (
    <div className="table-wrap">
      <table className="tbl">
        <thead>
          <tr>
            <th>{t("colCompany")}</th>
            <th>{t("colPlan")}</th>
            <th>{t("colSeats")}</th>
            <th>{t("colDocs")}</th>
            <th>{t("colStatus")}</th>
            <th style={{ textAlign: "right" }}>{t("colActions")}</th>
          </tr>
        </thead>
        <tbody>
          {COMPANIES.map((c) => (
            <tr key={c.id}>
              <td>
                <div className="fname">
                  <span className="ftype img">
                    <Building2 size={15} />
                  </span>
                  <span>
                    <div className="nm">{c.name}</div>
                    <div className="sz">{c.id}</div>
                  </span>
                </div>
              </td>
              <td className="mono-cell">{tPlans(c.planKey)}</td>
              <td className="mono-cell">{c.seats}</td>
              <td className="mono-cell">{c.docs.toLocaleString()}</td>
              <td>
                <Pill status={c.status} />
              </td>
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
        <span>{t("footCount", { count: COMPANIES.length })}</span>
      </div>
    </div>
  );
}
