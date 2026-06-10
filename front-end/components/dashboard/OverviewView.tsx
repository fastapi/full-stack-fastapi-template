"use client";

import { useTranslations } from "next-intl";
import StatCards from "@/components/dashboard/StatCards";
import ParseChart from "@/components/dashboard/ParseChart";
import ActivityFeed from "@/components/dashboard/ActivityFeed";
import { DOCS } from "@/lib/data";

export default function OverviewView() {
  const t = useTranslations("overview");
  return (
    <div>
      <StatCards />
      <div className="ov-grid">
        <div className="panel">
          <div className="panel-head">
            <div>
              <h3>{t("volumeTitle")}</h3>
              <div className="sub">{t("volumeSub")}</div>
            </div>
            <div className="chart-legend">
              <span>
                <i style={{ background: "var(--cyan)" }} /> {t("legendParsed")}
              </span>
              <span>
                <i style={{ background: "oklch(0.68 0.17 25)" }} /> {t("legendFailed")}
              </span>
            </div>
          </div>
          <div className="panel-body">
            <ParseChart />
          </div>
        </div>
        <div className="panel">
          <div className="panel-head">
            <div>
              <h3>{t("activityTitle")}</h3>
              <div className="sub">{t("activitySub")}</div>
            </div>
          </div>
          <ActivityFeed items={DOCS.slice(0, 5)} />
        </div>
      </div>
    </div>
  );
}
