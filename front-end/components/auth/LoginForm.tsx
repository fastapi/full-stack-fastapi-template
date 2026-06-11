"use client";

import { useTransition } from "react";
import { useLocale, useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { login } from "@/lib/actions";

export default function LoginForm() {
  const t = useTranslations("auth.login");
  const locale = useLocale();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();
  const error = searchParams.get("error");

  return (
    <form
      className="auth-form"
      action={(formData) => startTransition(() => void login(locale, formData))}
    >
      {error && <div className="field-error">{error === "unreachable" ? t("errorUnreachable") : t("error")}</div>}

      <div className="field">
        <label htmlFor="login-email">{t("email")}</label>
        <input
          id="login-email"
          name="email"
          type="email"
          required
          autoComplete="email"
          placeholder={t("emailPlaceholder")}
        />
      </div>

      <div className="field">
        <label htmlFor="login-password">{t("password")}</label>
        <input
          id="login-password"
          name="password"
          type="password"
          required
          autoComplete="current-password"
          placeholder={t("passwordPlaceholder")}
        />
      </div>

      <button type="submit" className="btn btn-primary" disabled={isPending}>
        {t("submit")}
      </button>
    </form>
  );
}
