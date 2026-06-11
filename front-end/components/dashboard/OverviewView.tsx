"use client";

import { useEffect, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import StatCards from "@/components/dashboard/StatCards";
import ParseChart from "@/components/dashboard/ParseChart";
import ActivityFeed from "@/components/dashboard/ActivityFeed";
import { apiMessage } from "@/lib/api";
import {
  FilesService,
  StoragesService,
  type FileWithJobPublic,
  type UserStorageStatPublic,
} from "@/lib/client";
import { jobStatus, toDocRow } from "@/lib/files";
import type { VolumePoint } from "@/lib/data";

/** Builds the 30-day parsed/failed series from the user's real file list. */
function buildVolume(files: FileWithJobPublic[]): VolumePoint[] {
  const days: VolumePoint[] = [];
  const byDay = new Map<string, VolumePoint>();
  const now = new Date();
  for (let i = 29; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    const key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
    const point = { day: `${d.getMonth() + 1}/${d.getDate()}`, parsed: 0, failed: 0 };
    byDay.set(key, point);
    days.push(point);
  }
  for (const f of files) {
    if (!f.created_at) continue;
    const d = new Date(f.created_at);
    const point = byDay.get(`${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`);
    if (!point) continue;
    if (jobStatus(f.job) === "fail") point.failed += 1;
    else point.parsed += 1;
  }
  return days;
}

export default function OverviewView() {
  const t = useTranslations("overview");
  const [stat, setStat] = useState<UserStorageStatPublic | null>(null);
  const [files, setFiles] = useState<FileWithJobPublic[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    Promise.all([StoragesService.getMyStorageStat(), FilesService.listFiles({ limit: 500 })])
      .then(([s, f]) => {
        if (!active) return;
        setStat(s);
        setFiles(f);
      })
      .catch((err) => active && setError(apiMessage(err)));
    return () => {
      active = false;
    };
  }, []);

  const volume = useMemo(() => buildVolume(files), [files]);
  const recent = useMemo(() => files.slice(0, 5).map(toDocRow), [files]);

  return (
    <div>
      {error && <div className="field-error">{error}</div>}
      <StatCards stat={stat} />
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
                <i style={{ background: "var(--bad)" }} /> {t("legendFailed")}
              </span>
            </div>
          </div>
          <div className="panel-body">
            <ParseChart data={volume} />
          </div>
        </div>
        <div className="panel">
          <div className="panel-head">
            <div>
              <h3>{t("activityTitle")}</h3>
              <div className="sub">{t("activitySub")}</div>
            </div>
          </div>
          <ActivityFeed items={recent} />
        </div>
      </div>
    </div>
  );
}
