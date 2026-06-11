"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiMessage } from "@/lib/api";
import { UsersService, type UserPublic } from "@/lib/client";
import { formatDate } from "@/lib/files";

const GRADIENTS = [
  "linear-gradient(135deg,oklch(0.82 0.14 205),oklch(0.82 0.14 75))",
  "linear-gradient(135deg,oklch(0.82 0.14 75),oklch(0.80 0.15 155))",
  "linear-gradient(135deg,oklch(0.80 0.15 155),oklch(0.82 0.14 205))",
  "linear-gradient(135deg,oklch(0.82 0.14 205),oklch(0.68 0.17 25))",
];

function initialsOf(user: UserPublic): string {
  const name = user.full_name?.trim() || user.email;
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]!.toUpperCase())
    .join("");
}

export default function UsersView() {
  const t = useTranslations("users");
  const tc = useTranslations("common");
  const [users, setUsers] = useState<UserPublic[]>([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    UsersService.readUsers({ limit: 100 })
      .then((res) => {
        if (!active) return;
        setUsers(res.data);
        setCount(res.count);
      })
      .catch((err) => active && setError(apiMessage(err)))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="table-wrap">
      {error && <div className="field-error">{error}</div>}
      <table className="tbl">
        <thead>
          <tr>
            <th>{t("colUser")}</th>
            <th>{t("colRole")}</th>
            <th>{t("colStatus")}</th>
            <th>{t("colCreated")}</th>
          </tr>
        </thead>
        <tbody>
          {loading && (
            <tr className="empty-row">
              <td colSpan={4}>{tc("loading")}</td>
            </tr>
          )}
          {!loading && users.length === 0 && (
            <tr className="empty-row">
              <td colSpan={4}>{t("empty")}</td>
            </tr>
          )}
          {users.map((u, i) => (
            <tr key={u.id}>
              <td>
                <div className="fname">
                  <span className="users-avatar" style={{ background: GRADIENTS[i % GRADIENTS.length] }}>
                    {initialsOf(u)}
                  </span>
                  <span>
                    <div className="nm">{u.full_name?.trim() || u.email.split("@")[0]}</div>
                    <div className="sz">{u.email}</div>
                  </span>
                </div>
              </td>
              <td className="mono-cell">{u.is_superuser ? t("roleAdmin") : t("roleUser")}</td>
              <td>
                <span className={`pill ${u.is_active ? "done" : "fail"}`}>
                  <span className="dot" />
                  {u.is_active ? t("active") : t("inactive")}
                </span>
              </td>
              <td className="mono-cell">{formatDate(u.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="table-foot">
        <span>{t("footCount", { count })}</span>
        <span />
      </div>
    </div>
  );
}
