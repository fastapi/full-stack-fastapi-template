"use client";

import { useTransition } from "react";
import { useLocale, useTranslations } from "next-intl";
import { signup } from "@/lib/actions";

export default function SignupForm() {
  const t = useTranslations("auth.signup");
  const locale = useLocale();
  const [isPending, startTransition] = useTransition();

  return (
    <form
      className="auth-form"
      action={(formData) => startTransition(() => void signup(locale, formData))}
    >
      <div className="field">
        <label htmlFor="signup-name">{t("name")}</label>
        <input
          id="signup-name"
          name="name"
          type="text"
          required
          autoComplete="name"
          placeholder={t("namePlaceholder")}
        />
      </div>

      <div className="field">
        <label htmlFor="signup-email">{t("email")}</label>
        <input
          id="signup-email"
          name="email"
          type="email"
          required
          autoComplete="email"
          placeholder={t("emailPlaceholder")}
        />
      </div>

      <div className="field">
        <label htmlFor="signup-password">{t("password")}</label>
        <input
          id="signup-password"
          name="password"
          type="password"
          required
          autoComplete="new-password"
          placeholder={t("passwordPlaceholder")}
        />
      </div>

      <div className="field">
        <label>{t("role")}</label>
        <div className="auth-role-options">
          <label className="auth-role-option">
            <input type="radio" name="role" value="user" defaultChecked />
            <span className="role-title">{t("roleUser")}</span>
            <span className="role-desc">{t("roleUserDesc")}</span>
          </label>
          <label className="auth-role-option">
            <input type="radio" name="role" value="company" />
            <span className="role-title">{t("roleCompany")}</span>
            <span className="role-desc">{t("roleCompanyDesc")}</span>
          </label>
        </div>
      </div>

      <button type="submit" className="btn btn-primary" disabled={isPending}>
        {t("submit")}
      </button>
    </form>
  );
}
