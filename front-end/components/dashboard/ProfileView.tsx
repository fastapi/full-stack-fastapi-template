"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import ActivityFeed from "@/components/dashboard/ActivityFeed";
import { apiMessage } from "@/lib/api";
import { FilesService, UsersService } from "@/lib/client";
import { toDocRow } from "@/lib/files";
import type { AuthUser } from "@/lib/auth";
import type { DocRow } from "@/lib/data";

export interface ProfileViewProps {
  user: AuthUser;
}

export default function ProfileView({ user }: ProfileViewProps) {
  const t = useTranslations("profile");
  const tc = useTranslations("common");
  const tShell = useTranslations("shell");
  const router = useRouter();

  const [fullName, setFullName] = useState(user.name);
  const [email, setEmail] = useState(user.email);
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileMsg, setProfileMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [savingPassword, setSavingPassword] = useState(false);
  const [passwordMsg, setPasswordMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const [recent, setRecent] = useState<DocRow[]>([]);

  useEffect(() => {
    let active = true;
    FilesService.listFiles({ limit: 5 })
      .then((files) => active && setRecent(files.map(toDocRow)))
      .catch(() => {});
    return () => {
      active = false;
    };
  }, []);

  const saveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingProfile(true);
    setProfileMsg(null);
    try {
      await UsersService.updateUserMe({
        requestBody: { full_name: fullName.trim() || null, email: email.trim() },
      });
      setProfileMsg({ ok: true, text: t("saved") });
      router.refresh();
    } catch (err) {
      setProfileMsg({ ok: false, text: apiMessage(err) });
    } finally {
      setSavingProfile(false);
    }
  };

  const savePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingPassword(true);
    setPasswordMsg(null);
    try {
      await UsersService.updatePasswordMe({
        requestBody: { current_password: currentPassword, new_password: newPassword },
      });
      setPasswordMsg({ ok: true, text: t("passwordSaved") });
      setCurrentPassword("");
      setNewPassword("");
    } catch (err) {
      setPasswordMsg({ ok: false, text: apiMessage(err) });
    } finally {
      setSavingPassword(false);
    }
  };

  return (
    <div className="settings-wrap">
      <form className="set-panel" onSubmit={saveProfile}>
        <div className="sp-head" style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <span className="sb-avatar" style={{ width: 44, height: 44, fontSize: 15 }}>
            {user.initials}
          </span>
          <div>
            <h3>{t("detailsTitle")}</h3>
            <p>{t("detailsSub")}</p>
          </div>
        </div>
        <div className="set-row">
          <div className="label">
            <div className="d" style={{ marginTop: 0 }}>
              {t("fieldName")}
            </div>
          </div>
          <input
            className="auth-input"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            aria-label={t("fieldName")}
          />
        </div>
        <div className="set-row">
          <div className="label">
            <div className="d" style={{ marginTop: 0 }}>
              {t("fieldEmail")}
            </div>
          </div>
          <input
            className="auth-input"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            aria-label={t("fieldEmail")}
          />
        </div>
        <div className="set-row">
          <div className="label">
            <div className="d" style={{ marginTop: 0 }}>
              {t("fieldRole")}
            </div>
          </div>
          <div className="t" style={{ fontFamily: "var(--font-mono)", fontSize: 13.5 }}>
            {tShell(
              user.role === "admin" ? "roleAdmin" : user.role === "company" ? "roleCompany" : "roleUser"
            )}
          </div>
        </div>
        <div className="set-row">
          <div className="label">
            {profileMsg && (
              <div className="d" style={{ marginTop: 0, color: profileMsg.ok ? "var(--ok)" : "var(--bad)" }}>
                {profileMsg.text}
              </div>
            )}
          </div>
          <button className="btn btn-primary" type="submit" disabled={savingProfile}>
            {savingProfile ? tc("loading") : tc("save")}
          </button>
        </div>
      </form>

      <form className="set-panel" onSubmit={savePassword}>
        <div className="sp-head">
          <h3>{t("passwordTitle")}</h3>
          <p>{t("passwordSub")}</p>
        </div>
        <div className="set-row">
          <div className="label">
            <div className="d" style={{ marginTop: 0 }}>
              {t("currentPassword")}
            </div>
          </div>
          <input
            className="auth-input"
            type="password"
            required
            autoComplete="current-password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            aria-label={t("currentPassword")}
          />
        </div>
        <div className="set-row">
          <div className="label">
            <div className="d" style={{ marginTop: 0 }}>
              {t("newPassword")}
            </div>
          </div>
          <input
            className="auth-input"
            type="password"
            required
            minLength={8}
            autoComplete="new-password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            aria-label={t("newPassword")}
          />
        </div>
        <div className="set-row">
          <div className="label">
            {passwordMsg && (
              <div className="d" style={{ marginTop: 0, color: passwordMsg.ok ? "var(--ok)" : "var(--bad)" }}>
                {passwordMsg.text}
              </div>
            )}
          </div>
          <button className="btn btn-primary" type="submit" disabled={savingPassword}>
            {savingPassword ? tc("loading") : t("changePassword")}
          </button>
        </div>
      </form>

      <div className="panel">
        <div className="panel-head">
          <div>
            <h3>{t("recentTitle")}</h3>
            <div className="sub">{t("recentSub")}</div>
          </div>
        </div>
        <ActivityFeed items={recent} />
      </div>
    </div>
  );
}
