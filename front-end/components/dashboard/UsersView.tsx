"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiMessage } from "@/lib/api";
import { UsersService, type UserPublic, type UserType } from "@/lib/client";
import { formatDate } from "@/lib/files";
import { USER_TYPES } from "@/constants";

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

  console.log('adduser',t("addUser"))
  const [newName, setNewName] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newType, setNewType] = useState<UserType>("company");
  const [creating, setCreating] = useState(false);
  const [createMsg, setCreateMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const createUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    setCreateMsg(null);
    try {
      const user = await UsersService.createUserEndpoint({
        requestBody: {
          email: newEmail.trim(),
          password: newPassword,
          full_name: newName.trim() || null,
          user_type: newType,
        },
      });
      setUsers((prev) => [user, ...prev]);
      setCount((c) => c + 1);
      setNewName("");
      setNewEmail("");
      setNewPassword("");
      setCreateMsg({ ok: true, text: t("created") });
    } catch (err) {
      setCreateMsg({ ok: false, text: apiMessage(err) });
    } finally {
      setCreating(false);
    }
  };

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
      <form className="users-create" onSubmit={createUser}>
        <input
          className="auth-input"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder={t("fieldName")}
          aria-label={t("fieldName")}
        />
        <input
          className="auth-input"
          type="email"
          required
          value={newEmail}
          onChange={(e) => setNewEmail(e.target.value)}
          placeholder={t("fieldEmail")}
          aria-label={t("fieldEmail")}
        />
        <input
          className="auth-input"
          type="password"
          required
          minLength={8}
          autoComplete="new-password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          placeholder={t("fieldPassword")}
          aria-label={t("fieldPassword")}
        />
        <select
          className="auth-input"
          value={newType}
          onChange={(e) => setNewType(e.target.value as UserType)}
          aria-label={t("fieldType")}
        >
          {USER_TYPES.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {t(opt.labelKey)}
            </option>
          ))}
        </select>
        <button className="btn btn-primary" type="submit" disabled={creating}>
          {creating ? tc("loading") : t("addUser")}
        </button>
        {createMsg && (
          <div className="field-error" style={createMsg.ok ? { color: "var(--ok)" } : undefined}>
            {createMsg.text}
          </div>
        )}
      </form>
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
              <td className="mono-cell">
                {u.user_type === "admin" || u.is_superuser
                  ? t("roleAdmin")
                  : u.user_type === "company"
                    ? t("roleCompany")
                    : t("roleUser")}
              </td>
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
